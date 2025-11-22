# network_of_interactive_nodes/core/managers/p2p_manager.py
'''
class P2PManager(INode):
    Gestor Principal de la Capa de Red (Router).

    Responsabilidad: 
    1. Componer los 'Handlers' solo si las dependencias necesarias existen.
    2. Enrutar mensajes solo a los handlers activos.

    Attributes:
        _sync_handler (SyncHandler | None): Maneja versión y headers (Si hay blockchain).
        _gossip_handler (GossipHandler | None): Maneja inv/tx/block (Si hay validador).
        _data_handler (DataHandler | None): Maneja getdata (Si hay blockchain y mempool).
'''

import logging
from typing import List, Tuple, Optional

# --- Interfaces y Transporte ---
from core.interfaces.i_node import INode 
from core.interfaces.i_node_roles import IBlockValidatorRole
from core.p2p.p2p_service import P2PService 
from core.p2p.peer import Peer 
from core.p2p.message import Message

# --- Modelos ---
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.models.transaction import Transaction
from core.mempool.mempool import Mempool

# --- Handlers (Deben importar sus versiones Estrictas, sin Optional) ---
from core.p2p.handlers.sync_handler import SyncHandler
from core.p2p.handlers.gossip_handler import GossipHandler
from core.p2p.handlers.data_handler import DataHandler

# --- DTOs ---
from core.p2p.payloads.version_payload import VersionPayload
from core.p2p.payloads.get_headers_payload import GetHeadersPayload
from core.p2p.payloads.headers_payload import HeadersPayload
from core.p2p.payloads.inv_payload import InvPayload
from core.p2p.payloads.get_data_payload import GetDataPayload
from core.p2p.payloads.block_payload import BlockPayload
from core.p2p.payloads.tx_payload import TxPayload


class P2PManager(INode):

    def __init__(self, 
                 validator_role: Optional[IBlockValidatorRole], 
                 blockchain: Optional[Blockchain],
                 mempool: Optional[Mempool],
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None):
        
        logging.info("P2P Manager: Configurando handlers dinámicamente...")
        
        # 1. Inicializar Transporte
        self._p2p_service = P2PService(self, host, port, seed_peers)

        # 2. Composición Condicional (Aquí está la solución)
        
        # A. SyncHandler (Necesita Blockchain, aunque sea ligera/stub)
        #    Si es SPV, 'blockchain' puede ser None o un objeto HeaderChain. 
        #    Asumiremos que si pasas None, no hay sync de bloques, solo handshake básico.
        self._sync_handler: Optional[SyncHandler] = None
        if blockchain is not None:
            self._sync_handler = SyncHandler(blockchain, self._p2p_service)
        
        # B. GossipHandler (Necesita Validador)
        self._gossip_handler: Optional[GossipHandler] = None
        if validator_role is not None:
            # Solo instanciamos si tenemos lógica de validación y estado donde guardar
            self._gossip_handler = GossipHandler(
                blockchain=blockchain, # Puede ser None dentro del handler si se permite
                mempool=mempool,
                p2p_service=self._p2p_service,
                validator_role=validator_role
            )
        
        # C. DataHandler (ESTRICTO: Necesita Blockchain Y Mempool)
        self._data_handler: Optional[DataHandler] = None
        if blockchain is not None and mempool is not None:
            self._data_handler = DataHandler(
                blockchain=blockchain,
                mempool=mempool,
                p2p_service=self._p2p_service
            )
        
        logging.info(f"P2P Manager listo. Handlers activos: Sync={bool(self._sync_handler)}, Gossip={bool(self._gossip_handler)}, Data={bool(self._data_handler)}")

    # --- Ciclo de Vida ---

    async def start(self) -> None:
        await self._p2p_service.start_service()

    async def stop(self) -> None:
        await self._p2p_service.stop_service()

    # --- Router Protegido ---

    def handle_message(self, message: Message, peer_id: str) -> None: 
        command = message.command
        payload = message.payload 
        peer = self._p2p_service.get_peer(peer_id)
        if not peer: return

        try:
            # GRUPO 1: Sincronización (Solo si el handler existe)
            if self._sync_handler:
                if command == 'version' and isinstance(payload, VersionPayload):
                    self._sync_handler.handle_version(payload, peer)
                    
                elif command == 'getheaders' and isinstance(payload, GetHeadersPayload):
                    self._sync_handler.handle_get_headers(payload, peer)

                elif command == 'headers' and isinstance(payload, HeadersPayload):
                    self._sync_handler.handle_headers(payload, peer)
            
            # GRUPO 2: Datos (Solo si tenemos datos para servir)
            if self._data_handler:
                if command == 'getdata' and isinstance(payload, GetDataPayload):
                    self._data_handler.handle_get_data(payload, peer)
                
            # GRUPO 3: Chisme (Solo si podemos validar)
            if self._gossip_handler:
                if command == 'inv' and isinstance(payload, InvPayload):
                    self._gossip_handler.handle_inv(payload, peer)

                elif command == 'block' and isinstance(payload, BlockPayload):
                    self._gossip_handler.handle_block(payload, peer_id)

                elif command == 'tx' and isinstance(payload, TxPayload):
                    self._gossip_handler.handle_tx(payload, peer_id)
                
        except Exception as e:
            logging.error(f"P2P Router Error: {command} -> {e}")

    # --- Delegación Protegida ---

    def initiate_handshake(self, peer: Peer) -> None:
        if self._sync_handler:
            self._sync_handler.initiate_handshake(peer)

    def broadcast_new_block(self, block: Block) -> None:
        if self._gossip_handler:
            self._gossip_handler.broadcast_new_block(block)

    def broadcast_new_tx(self, tx: Transaction) -> None:
        if self._gossip_handler:
            self._gossip_handler.broadcast_new_tx(tx)