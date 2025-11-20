#   core/nodes/wallet_node.py
'''
class WalletNode:
    Fachada (Facade) que implementa un Nodo Billetera (Wallet).
    
    Responsabilidad:
        1. Gestión de Identidad: Carga claves y configura el WalletManager.
        2. Composición de Red: Instancia un nodo base (FullNode) para conectarse.
        3. Operativa: Provee métodos fáciles para crear y difundir transacciones.

    Attributes:
        _wallet_manager (WalletManager): Gestor de identidad y firma.
        _node (FullNode): El motor de red subyacente.

    Methods:
        start(): Inicia el nodo de red.
        stop(): Detiene el nodo de red.
        get_address(): Retorna la dirección propia.
        
        send_data_transaction(data_type, content, metadata): 
            Método de alto nivel para usuarios. Crea, firma y difunde.
'''

import logging
import time
from typing import Dict, List, Tuple, Optional, Any
from Crypto.PublicKey.ECC import EccKey

# --- Importaciones de Componentes de Identidad ---
from core.managers.wallet_manager import WalletManager
from core.client_services.software_signer import SoftwareSigner
from identity.key_persistence import KeyPersistence

# --- Importaciones de Infraestructura de Red ---
from core.nodes.full_node import FullNode

# --- Importaciones de Modelos y Fábricas ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager
from core.dto.data_entry_creation_params import DataEntryCreationParams
from core.factories.data_entry_factory import DataEntryFactory

class WalletNode:

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool,
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None,
                 wallet_file: str = 'mi_billetera.pem',
                 persistence_manager: Any = None):
        
        logging.info("Inicializando Wallet Node (Full Mode)...")

        # 1. GESTIÓN DE IDENTIDAD
        private_key = KeyPersistence.ensure_key_exists(wallet_file)
        self._signer = SoftwareSigner(private_key)
        
        self._wallet_manager = WalletManager(
            public_key=private_key.public_key(),
            signer=self._signer
        )

        # 2. COMPOSICIÓN DE RED
        self._node = FullNode(
            blockchain=blockchain,
            consensus_manager=consensus_manager,
            public_key_map=public_key_map,
            mempool=mempool,
            host=host,
            port=port,
            seed_peers=seed_peers,
            persistence_manager=persistence_manager
        )
        
        logging.info(f"Wallet Node listo. Dirección: {self._wallet_manager.get_address()}")

    # --- Ciclo de Vida ---

    async def start(self) -> None:
        logging.info(">>> ARRANCANDO WALLET NODE <<<")
        await self._node.start()
        logging.info(">>> WALLET SINCRONIZADA Y LISTA <<<")

    async def stop(self) -> None:
        logging.info(">>> CERRANDO WALLET NODE <<<")
        await self._node.stop()

    # --- Métodos de Usuario ---

    def get_address(self) -> str:
        return self._wallet_manager.get_address()

    # CORRECCIÓN APLICADA AQUÍ: Tipado correcto y eliminación de código muerto
    def send_data_transaction(self, 
                              data_type: str, 
                              content: str, 
                              metadata: Optional[Dict[str, Any]] = None) -> bool:
        '''
        Crea, firma y envía una transacción de datos a la red.
        '''
        if metadata is None:
            metadata = {}

        logging.info(f"Wallet: Iniciando envío de datos '{data_type}'...")
        
        try:
            # 1. Crear el Payload de Datos (DataEntry)
            #    Usamos las factorías del Núcleo Estático.
            #    (Se eliminó la variable 'content_bytes' que no se usaba)
            
            entry_params = DataEntryCreationParams(
                source_id=self.get_address(),
                data_type=data_type,
                value=content.encode('utf-8'), # Convertimos el string a bytes directamente
                nonce=int(time.time()),
                metadata=metadata
            )
            entry = DataEntryFactory.create(entry_params)

            # 2. Firmar la Transacción (Usando el WalletManager)
            signed_tx = self._wallet_manager.create_and_sign_data([entry])

            # 3. Difundir a la Red (Usando el P2PManager del Nodo interno)
            validation_manager = self._node.get_validation_manager()
            
            if validation_manager.validate_tx_rules(signed_tx):
                p2p_manager = self._node.get_p2p_manager()
                p2p_manager.broadcast_new_tx(signed_tx)
                
                logging.info(f"Wallet: Transacción {signed_tx.tx_hash[:6]} enviada exitosamente.")
                return True
            else:
                logging.error("Wallet: La transacción fue rechazada por reglas internas.")
                return False

        except Exception as e:
            logging.error(f"Wallet: Error enviando transacción: {e}")
            return False