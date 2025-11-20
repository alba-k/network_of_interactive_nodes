'''
class FullNode:
    Representa un Nodo Completo en la red.
    
    Actúa como un "Contenedor de Composición" (Container) que instancia, conecta y coordina a los Gestores especializados (Capa 2).

    Responsabilidades:
        1. Inicialización: Crea las instancias de ValidationManager y P2PManager.
        2. Inyección de Dependencias: Conecta el Validador dentro del Gestor P2P.
        3. Ciclo de Vida: Inicia (start) y detiene (stop) los subsistemas en orden.
        4. Acceso: Provee acceso a los gestores para las subclases (Miner/Gateway).

    Attributes:
        _blockchain (Blockchain): El modelo de datos (Estado de la cadena).
        _mempool (Mempool): El estado de las transacciones (Gestor de Colección).
        _consensus_manager (ConsensusManager): Lógica base de consenso.
        
        _validation_manager (ValidationManager): (Gestor Capa 2) Se encarga de validar reglas de negocio y actualizar el estado.
        _p2p_manager (P2PManager): (Gestor Capa 2) Se encarga de la comunicación de red y sincronización.
        _persistence_manager (Any): (Placeholder) Futuro gestor para guardar/cargar de disco.

    Methods:
        start(self) -> None: Inicia los servicios del nodo (principalmente P2PManager).
        stop(self) -> None: Detiene los servicios del nodo de forma segura.
        get_p2p_manager(self) -> P2PManager: (Getter) Permite acceso al gestor P2P (usado por MinerNode/GatewayNode).
        get_validation_manager(self) -> ValidationManager: (Getter) Permite acceso al gestor de validación (usado por MinerNode).
        get_blockchain(self) -> Blockchain: (Getter) Acceso al modelo de blockchain.
        get_mempool(self) -> Mempool: (Getter) Acceso al mempool.
'''

import logging
from typing import Dict, List, Tuple, Optional, Any
from Crypto.PublicKey.ECC import EccKey

# --- Importaciones de Modelos y Gestores de Estado Base ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

# --- Importaciones de los Nuevos Gestores (Capa 2) ---
from core.managers.validation_manager import ValidationManager
from core.managers.p2p_manager import P2PManager
# from core.managers.persistence_manager import PersistenceManager (Futuro)

class FullNode:

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool,
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None,
                 persistence_manager: Any = None):
        
        # 1. Guardar referencias al Estado Base (Modelos en Memoria)
        self._blockchain = blockchain
        self._consensus_manager = consensus_manager
        self._mempool = mempool
        
        # 2. Gestor de Persistencia (Disco) - Placeholder
        self._persistence_manager = persistence_manager

        # --- ALERTA DE DESARROLLO: FALTA PERSISTENCIA Y UTXO ---
        if self._persistence_manager is None:
            logging.warning("!!! EJECUTANDO EN MODO MEMORIA (VOLÁTIL) !!!")
            logging.warning(">> FALTA: Implementar PersistenceManager (LevelDB/RocksDB).")
            logging.warning(">> FALTA: Implementar UTXO Set (Validación rápida).")
            logging.warning(">> FALTA: Implementar Lógica de 'Pruning' (Poda).")
            logging.warning("Si apagas el nodo, perderás toda la Blockchain.")
        # -------------------------------------------------------

        # 3. Composición: Instanciar el Gestor de Validación (Capa 2).
        #    Este gestor encapsula la lógica de aceptar bloques y TXs.
        self._validation_manager = ValidationManager(
            consensus_manager=self._consensus_manager,
            mempool=self._mempool,
            public_key_map=public_key_map
        )
        
        # 4. Composición: Instanciar el Gestor P2P (Capa 2).
        #    Aquí ocurre la MAGIA de la composición:
        #    Le inyectamos 'validator_role=self._validation_manager'.
        #    Así, el P2PManager sabe a quién llamar cuando llega un bloque, sin saber CÓMO se valida.
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
        # 1. (Futuro) Iniciar persistencia (cargar bloques de disco)
        if self._persistence_manager:
            logging.info('Iniciando persistencia...')
            # TODO: Implementar carga de cadena: await self._persistence_manager.load_chain()
            # TODO: Implementar reconstrucción de UTXO Set.

        # 2. Iniciar Red (Delegar al P2PManager)
        logging.info('Full Node iniciando servicios de red...')
        await self._p2p_manager.start()
        
        logging.info('Full Node operando.')

    async def stop(self) -> None:
        # 1. Detener Red primero (dejar de recibir datos nuevos)
        logging.info('Full Node deteniendo servicios de red...')
        await self._p2p_manager.stop()

        # 2. (Futuro) Cerrar persistencia (guardar estado final)
        if self._persistence_manager:
            logging.info('Cerrando persistencia...')
            # TODO: Implementar cierre seguro: await self._persistence_manager.close()

        logging.info('Full Node detenido.')

    # --- Getters para Subclases (Herencia) ---
    # Estos métodos son esenciales porque MinerNode y GatewayNode heredan de aquí
    # y necesitan interactuar con los componentes internos.

    def get_p2p_manager(self) -> P2PManager:
        return self._p2p_manager

    def get_validation_manager(self) -> ValidationManager:
        return self._validation_manager
    
    def get_blockchain(self) -> Blockchain:
        return self._blockchain
    
    def get_mempool(self) -> Mempool:
        return self._mempool