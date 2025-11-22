# core/p2p/handlers/gossip_handler.py
'''
class GossipHandler:
    Estrategia (Handler) especializada en la Propagación (Gossip) de datos.
    
    Responsabilidad:
        1. Manejar anuncios ('inv'): Decidir qué pedir.
        2. Manejar recepción de datos ('block', 'tx'): Deserializar, Validar y Retransmitir.
        3. Iniciar la difusión de datos propios (minados o creados).

    Attributes:
        _blockchain (Blockchain): Para verificar si ya tenemos un bloque.
        _mempool (Mempool): Para verificar si ya tenemos una TX.
        _p2p_service (P2PService): Transporte para enviar mensajes.
        _validator_role (IBlockValidatorRole): El Gestor de Consenso para validar reglas.

    Methods:
        handle_inv(payload, peer): Procesa inventarios y pide lo que falta via 'getdata'.
        
        handle_block(payload, peer_id): 
            1. Deserializa. 
            2. Delega al Validador. 
            3. Si es válido, hace broadcast.
            
        handle_tx(payload, peer_id): 
            1. Deserializa. 
            2. Delega al Validador. 
            3. Si es válida, hace broadcast.
            
        broadcast_new_block(block): Crea un 'inv' y lo envía a todos.
        broadcast_new_tx(tx): Crea un 'inv' y lo envía a todos.
'''

import logging
import asyncio
from typing import List, Optional

# --- Importaciones de Interfaces y Estado ---
from core.interfaces.i_node_roles import IBlockValidatorRole
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.models.transaction import Transaction
from core.mempool.mempool import Mempool

# --- Importaciones de P2P ---
from core.p2p.p2p_service import P2PService
from core.p2p.peer import Peer
from core.p2p.payloads.inv_payload import InvPayload
from core.p2p.payloads.get_data_payload import GetDataPayload
from core.p2p.payloads.block_payload import BlockPayload
from core.p2p.payloads.tx_payload import TxPayload
from core.p2p.payloads.inv_vector import InvVector

# --- Importaciones del Núcleo Estático ---
from core.deserializers.block_deserializer import BlockDeserializer
from core.deserializers.transaction_deserializer import TransactionDeserializer

class GossipHandler:

    def __init__(self, 
                 blockchain: Optional[Blockchain], 
                 mempool: Optional[Mempool], 
                 p2p_service: P2PService,
                 validator_role: Optional[IBlockValidatorRole]):
        
        self._blockchain = blockchain
        self._mempool = mempool
        self._p2p_service = p2p_service
        self._validator_role = validator_role
        
        logging.info("GossipHandler (Servicio de Propagación) inicializado.")

    # --- Handlers de Recepción (Entrada) ---

    def handle_inv(self, payload: InvPayload, peer: Peer) -> None:
        '''Recibimos un anuncio de datos. Decidir qué pedir.'''
        
        items_to_request: List[InvVector] = []
        
        for item in payload.inventory:
            # Tipo 2: Bloque
            if item.type == 2:
                if self._blockchain and not self._have_block(item.hash):
                    items_to_request.append(item)

            # Tipo 1: Transacción
            elif item.type == 1:
                if self._mempool and not self._mempool.have_transaction(item.hash):
                    items_to_request.append(item)
                
        if items_to_request:
            logging.info(f"Gossip: {peer.host} anunció {len(items_to_request)} items nuevos. Solicitando...")
            get_data_payload = GetDataPayload(inventory=items_to_request)
            asyncio.create_task(
                self._p2p_service.send_message(peer, 'getdata', get_data_payload)
            )

    def handle_block(self, payload: BlockPayload, peer_id: str) -> None:
        '''Recibimos un bloque completo. Validar y propagar.'''
        
        # Protección: Si no tenemos validador (SPV), ignoramos.
        if self._validator_role is None: return

        try:
            # 1. Deserializar (Núcleo Estático)
            block_obj = BlockDeserializer.from_dict(payload.block_data)
            
            # 2. Validar Reglas de Consenso (Delegar al Gestor)
            is_accepted = self._validator_role.validate_block_rules(block_obj)
            
            # 3. Si es válido y nuevo, propagar (Gossip)
            if is_accepted:
                logging.info(f"Gossip: Bloque {block_obj.index} válido recibido de {peer_id}. Propagando.")
                self.broadcast_new_block(block_obj)
        
        except (ValueError, TypeError) as e:
            logging.warning(f"Gossip: {peer_id} envió un bloque corrupto. {e}")

    def handle_tx(self, payload: TxPayload, peer_id: str) -> None:
        '''Recibimos una TX completa. Validar y propagar.'''
        
        # Protección: Si no tenemos validador (SPV), ignoramos.
        if self._validator_role is None: return

        try:
            # 1. Deserializar (Núcleo Estático)
            tx_obj = TransactionDeserializer.from_dict(payload.tx_data)
            
            # 2. Validar Reglas de TX (Delegar al Gestor)
            is_accepted = self._validator_role.validate_tx_rules(tx_obj)
            
            # 3. Si es válida y nueva, propagar (Gossip)
            if is_accepted:
                logging.info(f"Gossip: TX {tx_obj.tx_hash[:6]} válida recibida de {peer_id}. Propagando.")
                self.broadcast_new_tx(tx_obj)
        
        except (ValueError, TypeError) as e:
            logging.warning(f"Gossip: {peer_id} envió una TX corrupta. {e}")

    # --- Métodos Públicos de Difusión (Salida) ---

    def broadcast_new_block(self, block: Block) -> None:
        '''Anunciar un bloque propio (minado) a la red.'''
        inv_vector = InvVector(type=2, hash=block.hash)
        inv_payload = InvPayload(inventory=[inv_vector])
        asyncio.create_task(self._p2p_service.broadcast('inv', inv_payload))

    def broadcast_new_tx(self, tx: Transaction) -> None:
        '''Anunciar una TX propia (creada) a la red.'''
        inv_vector = InvVector(type=1, hash=tx.tx_hash)
        inv_payload = InvPayload(inventory=[inv_vector])
        asyncio.create_task(self._p2p_service.broadcast('inv', inv_payload))

    # --- Helpers ---

    def _have_block(self, block_hash: str) -> bool:
        # Busca en la cadena (lineal o indexado)
        if not self._blockchain: return False
        for b in reversed(self._blockchain.chain):
            if b.hash == block_hash: return True
        return False