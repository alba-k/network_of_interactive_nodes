# network_of_interactive_nodes/core/nodes/wallet_node.py
'''
class WalletNode(INode, IWalletRole):
    Implementa un "Rol" (Abstracción) de Billetera pura.
    No participa en la red P2P (INode es un 'stub'), solo sabe firmar transacciones.
    
    Attributes:
        _private_key (EccKey): La clave privada de este nodo (para firmar).
        _public_key  (EccKey): La clave pública derivada (para identidad).
    
    Methods:
        start(): (INode Stub) Método vacío. No inicia servicios.
        
        stop(): (INode Stub) Método vacío. No detiene servicios.
        
        handle_message(): (INode Stub) Método vacío. No procesa mensajes P2P.
        
        initiate_handshake(): (INode Stub) Método vacío. No inicia handshakes.

        create_and_sign_data(entries): (IWalletRole) Orquesta la firma de DataEntry.
            1. Calcular tamaño (Delega a TransactionUtils).
            2. Crear TX sin firmar (Delega a TransactionFactory).
            3. Firmar el hash (Delega a TransactionSigner).
            4. Crear TX firmada (Delega a TransactionFactory).
            5. Validar que el hash no cambió (Firma "Paranoica").
            6. Retornar la TX firmada.
'''

import logging
import time
from typing import List

# Importaciones de la Arquitectura
from core.interfaces.i_node import INode
from core.interfaces.i_node_roles import IWalletRole
from core.models.transaction import Transaction
from core.models.data_entry import DataEntry
from Crypto.PublicKey.ECC import EccKey
from core.security.transaction_signer import TransactionSigner
from core.factories.transaction_factory import TransactionFactory
from core.dto.transaction_creation_params import TransactionCreationParams
from core.utils.transaction_utils import TransactionUtils
from core.p2p.message import Message
from core.p2p.peer import Peer 

class WalletNode(INode, IWalletRole):

    def __init__(self, private_key: EccKey):
        self._private_key = private_key
        self._public_key = private_key.public_key()
        logging.info('Wallet Node (Billetera) inicializado.')

    async def start(self) -> None: pass

    async def stop(self) -> None: pass 

    def handle_message(self, message: Message, peer_id: str) -> None: pass

    def initiate_handshake(self, peer: Peer) -> None: pass

    
    def create_and_sign_data(self, entries: List[DataEntry]) -> Transaction:

        current_timestamp: float = time.time()
        
        size_bytes: int = TransactionUtils.calculate_data_size(entries)
        
        params_no_sig = TransactionCreationParams(
            entries = entries, 
            timestamp = current_timestamp, 
            signature = None,
            fee = 0, 
            size_bytes = size_bytes, 
            fee_rate = 0.0
        )
        unsigned_tx: Transaction = TransactionFactory.create(params_no_sig)
        
        signature_hex: str = TransactionSigner.sign(
            private_key=self._private_key, tx_hash=unsigned_tx.tx_hash
        )
        
        params_with_sig = TransactionCreationParams(
            entries=entries, timestamp=current_timestamp, signature=signature_hex,
            fee=0, size_bytes=size_bytes, fee_rate=0.0
        )
        signed_tx: Transaction = TransactionFactory.create(params_with_sig)
        
        if signed_tx.tx_hash != unsigned_tx.tx_hash:
             raise RuntimeError('Error de firma: El Hash cambió (WalletNode).')
             
        return signed_tx