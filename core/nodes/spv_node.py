# core/nodes/spv_node.py
'''
class SPVNode:
    Fachada (Facade) que implementa un Cliente Ligero (SPV).
    
    ADAPTACIÓN PARA TIPADO ESTRICTO:
    Como P2PManager exige recibir un Validator, Blockchain y Mempool reales (no None),
    este nodo instancia versiones "Stub" (vacías/dummy) para satisfacer el contrato
    sin cargar la lógica pesada.

    Attributes:
        _wallet_manager (WalletManager): Gestor de identidad.
        _p2p_manager (P2PManager): Gestor de red.
        _headers (List[Dict]): Almacenamiento local solo de encabezados.

    Methods:
        start(): Inicia red.
        stop(): Detiene red.
        verify_transaction(...): Verifica criptográficamente una TX.
'''

import logging
from typing import Dict, List, Tuple, Optional, Any

# Importaciones de Componentes ---
from core.managers.wallet_manager import WalletManager
from core.client_services.software_signer import SoftwareSigner
from identity.key_persistence import KeyPersistence

# Importaciones de Red ---
from core.interfaces.i_node import INode
from core.managers.p2p_manager import P2PManager
from core.p2p.message import Message
from core.p2p.peer import Peer

# Importaciones para Stubs (Cumplir contrato P2PManager) ---
from core.interfaces.i_node_roles import IBlockValidatorRole
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.models.transaction import Transaction
from core.mempool.mempool import Mempool

# Importaciones del Núcleo Estático ---
from core.validators.merkle_proof_validator import MerkleProofValidator 


# === CLASE STUB INTERNA (Para engañar al P2PManager de forma segura) ===
class _SPVValidatorStub(IBlockValidatorRole):
    '''
    Implementación vacía del validador.
    El SPV no valida bloques completos ni transacciones de terceros.
    '''
    def validate_block_rules(self, block: Block) -> bool:
        return False # Rechazar/Ignorar cualquier bloque completo recibido
    
    def validate_tx_rules(self, tx: Transaction) -> bool:
        return False # Rechazar/Ignorar cualquier TX recibida


class SPVNode(INode):

    def __init__(self, 
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None,
                 wallet_file: str = 'mi_billetera.pem'):
        
        logging.info("Inicializando SPV Node (Light Client)...")

        # 1. GESTIÓN DE IDENTIDAD
        private_key = KeyPersistence.ensure_key_exists(wallet_file)
        self._signer = SoftwareSigner(private_key)
        
        self._wallet_manager = WalletManager(
            public_key=private_key.public_key(),
            signer=self._signer
        )

        # 2. ESTADO LIGERO
        self._headers: List[Dict[str, Any]] = []
        
        # 3. CREACIÓN DE STUBS (Para satisfacer el tipado estricto de P2PManager)
        #    Creamos objetos reales pero vacíos. Son baratos en memoria.
        self._stub_blockchain = Blockchain()      # Cadena vacía
        self._stub_mempool = Mempool()            # Mempool vacío
        self._stub_validator = _SPVValidatorStub() # Validador que devuelve False

        # 4. COMPOSICIÓN DE RED
        #    Le pasamos los Stubs. El P2PManager estará feliz porque recibe los tipos correctos,
        #    pero el nodo seguirá siendo ligero porque estos objetos no harán nada.
        self._p2p_manager = P2PManager(
            validator_role=self._stub_validator, 
            blockchain=self._stub_blockchain,     
            mempool=self._stub_mempool,        
            host=host,
            port=port,
            seed_peers=seed_peers
        )
        
        logging.info(f"SPV Node listo. Wallet ID: {self._wallet_manager.get_address()}")

    # --- Ciclo de Vida ---

    async def start(self) -> None:
        logging.info(">>> ARRANCANDO SPV NODE (SOLO HEADERS) <<<")
        await self._p2p_manager.start()

    async def stop(self) -> None:
        logging.info(">>> DETENIENDO SPV NODE <<<")
        await self._p2p_manager.stop()
    
    # --- Implementación de INode (Delegación) ---
    
    def handle_message(self, message: Message, peer_id: str) -> None:
        self._p2p_manager.handle_message(message, peer_id)

    def initiate_handshake(self, peer: Peer) -> None:
        self._p2p_manager.initiate_handshake(peer)

    # --- Funcionalidad Específica SPV ---

    def verify_transaction(self, tx_hash: str, merkle_root: str, proof_path: List[str]) -> bool:
        logging.info(f"SPV: Verificando TX {tx_hash[:6]}...")
        is_valid = MerkleProofValidator.verify_proof(tx_hash, merkle_root, proof_path)
        
        if is_valid:
            logging.info("✅ SPV: Verificación Exitosa.")
        else:
            logging.warning("❌ SPV: Verificación Fallida.")
        return is_valid

    # --- Getters ---
    
    def get_wallet_manager(self) -> WalletManager:
        return self._wallet_manager
        
    def get_p2p_manager(self) -> P2PManager:
        return self._p2p_manager     