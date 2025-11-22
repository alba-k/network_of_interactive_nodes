# network_of_interactive_nodes/core/nodes/full_node.py
'''
class FullNode:
    Representa un Nodo Completo en la red.
    
    *** CORRECCIÓN: Usa blockchain.replace_chain() para cargar datos del disco. ***
'''

import logging
from typing import Dict, List, Tuple, Optional
from Crypto.PublicKey.ECC import EccKey

# --- Importaciones de Modelos y Gestores Base ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

# --- Importaciones de Gestores (Capa 2) ---
from core.managers.validation_manager import ValidationManager
from core.managers.p2p_manager import P2PManager
from core.managers.persistence_manager import PersistenceManager

class FullNode:

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool,
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None,
                 persistence_manager: Optional[PersistenceManager] = None):
        
        self._blockchain = blockchain
        self._consensus_manager = consensus_manager
        self._mempool = mempool
        self._persistence_manager = persistence_manager

        self._validation_manager = ValidationManager(
            consensus_manager=self._consensus_manager,
            mempool=self._mempool,
            public_key_map=public_key_map
        )
        
        self._p2p_manager = P2PManager(
            validator_role=self._validation_manager, 
            blockchain=blockchain,
            mempool=mempool,
            host=host,
            port=port,
            seed_peers=seed_peers
        )
        
        logging.info('Full Node (Contenedor) inicializado. Gestores listos.')

    async def start(self) -> None:
        
        # 1. Iniciar Persistencia (Cargar estado previo)
        if self._persistence_manager:
            logging.info('Persistencia: Verificando historial en disco...')
            loaded_chain = self._persistence_manager.load_chain()
            
            if loaded_chain:
                # -------------------------------------------------------------
                # [FIX] Usamos el método setter explícito, no la propiedad.
                # Esto soluciona el error "Attribute is read-only".
                # -------------------------------------------------------------
                self._blockchain.replace_chain(loaded_chain.chain)
                
                logging.info(f"Persistencia: Estado restaurado ({len(self._blockchain.chain)} bloques).")
            else:
                logging.info("Persistencia: No se encontró historial. Iniciando cadena nueva (Génesis).")

        # 2. Iniciar Red
        logging.info('Full Node iniciando servicios de red...')
        await self._p2p_manager.start()
        
        logging.info('Full Node operando.')

    async def stop(self) -> None:
        logging.info('Full Node deteniendo servicios de red...')
        await self._p2p_manager.stop()

        if self._persistence_manager:
            logging.info('Persistencia: Guardando estado en disco...')
            success = self._persistence_manager.save_chain(self._blockchain)
            if success:
                logging.info("Persistencia: Estado guardado exitosamente.")
            else:
                logging.error("Persistencia: Error crítico al guardar el estado.")

        logging.info('Full Node detenido.')

    # --- Getters ---
    def get_p2p_manager(self) -> P2PManager:
        return self._p2p_manager

    def get_validation_manager(self) -> ValidationManager:
        return self._validation_manager
    
    def get_blockchain(self) -> Blockchain:
        return self._blockchain
    
    def get_mempool(self) -> Mempool:
        return self._mempool