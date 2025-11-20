# network_of_interactive_nodes/core/nodes/full_node.py
'''
class FullNode(INode, IBlockValidatorRole):
    Responsable de mantener la Blockchain completa, validar todas las transacciones y bloques, y participar en la red P2P.

    Attributes:
        _blockchain         (Blockchain):           La instancia del contenedor puro de la cadena.
        _consensus_manager  (ConsensusManager):     Servicio que aplica las reglas de consenso.
        _public_key_map     (Dict[str, EccKey]):    Mapa para la verificación de firmas.
        _mempool            (Mempool):              Contenedor para transacciones no confirmadas.
        _p2p_service        (P2PService):           Capa de comunicación con otros nodos.
    
    Methods:
        start(): Iniciar los servicios asíncronos del nodo.
            1. Indicar al P2PService que se inicie
            2. 


        stop(): Detener los servicios del nodo.
            1. Indicar al P2PService que se detenga
            2.
            
        handle_message(message, peer_id): (Router) Maneja un mensaje P2P entrante.
            1. Obtener datos del mensaje
            2. Validar que el Peer existe
            3. Enrutar el mensaje al handler correspondiente

        initiate_handshake(peer): (Acción) Inicia el handshake 'version'.
            1. Crear el payload 'version'
            2. Enviar el mensaje 'version'
        
        validate_block_rules(block): Valida un bloque completo.

        validate_tx_rules(tx): Valida una transacción.
        
        _handle_version_handshake(payload, peer): Procesa un 'version'.
            1. Comparar alturas
            2. Si el par está más adelantado, pedirle headers

        _send_get_headers(self, peer: Peer): (Acción) Pide 'headers' a un par.
            1. Crear un 'locator' (lista de hashes que tenemos)
            2. Crear el payload 'getheaders'
            3. Enviar el mensaje

        _handle_get_headers(payload, peer): Procesa un 'getheaders'.
            1. Encontrar los últimos 10 headers que tenemos
            2. Serializar solo el header
            3. Enviar los headers en un mensaje 'headers'

        _handle_headers(payload): Procesa un 'headers'.
            1. Validar la cadena
            2. Preparar la solicitud de bloques
            3. Delegar la acción de red (getdata)

        _handle_inv(payload, peer): Procesa un 'inv'.
            1. Revisar el inventario que nos anuncian
            2. Si es un bloque (tipo 2) y no lo tenemos, pedirlo
            3. Si es una TX (tipo 1) y no la tenemos, pedirla
            4. Si hay algo que pedir, enviar 'getdata'

        _handle_get_data(payload, peer): Procesa un 'getdata'.
            1. Revisar los items que nos piden
            2. Si piden un Bloque (tipo 2)
            3. Serializar y enviar el bloque
            4. Si piden una TX (tipo 1)
            5. Serializar y enviar la TX

        _broadcast_new_block(self, block: Block):
            1. Crear un 'inv' para este bloque
            2. Hacer broadcast del 'inv'

        _broadcast_new_tx(self, tx: Transaction):
            1. Crear un 'inv' para esta TX
            2. Hacer broadcast del 'inv'

        validate_block_rules(self, block: Block) -> bool:
            1. Deferir al ConsensusManager (que valida PoW, firmas, etc.)
            2. Si el bloque es válido y nuevo
            3. Propagarlo (Gossip)
            4. Limpiar la Mempool
        
        validate_tx_rules(self, tx: Transaction) -> bool:
            1. Validar integridad (hash)
            2. Validar firma (si la tiene)
            3. Añadir a la Mempool
            4. Si es nueva, propagarla (Gossip)


        _get_current_height(self) -> int: Obtiene el índice (altura) del último bloque.

        _get_block_by_index(self, index: int) -> Block | None: Obtiene un bloque por su índice (posición) en la cadena.

        _get_block_hash_by_index(self, index: int) -> str | None: Obtiene solo el hash de un bloque usando su índice.

        _get_block_by_hash(self, block_hash: str) -> Block | None: Obtiene un objeto Bloque completo buscando por su hash.

        _have_block(self, block_hash: str) -> bool: Verifica (True/False) si un bloque ya existe en la cadena.
        
'''

import logging
import time
import asyncio 
from typing import Dict, List, Tuple, Any, Optional # <-- Añadido Optional
from Crypto.PublicKey.ECC import EccKey

# ... (El resto de tus importaciones son correctas) ...
from core.interfaces.i_node import INode 
from core.interfaces.i_node_roles import IBlockValidatorRole
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.models.transaction import Transaction
from core.consensus.consensus_manager import ConsensusManager
from core.validators.transaction_validator import TransactionValidator
from core.validators.transaction_verifier import TransactionVerifier
from core.mempool.mempool import Mempool
from core.serializers.transaction_serializer import TransactionSerializer
from core.p2p.message import Message 
from core.p2p.peer import Peer 
from core.p2p.p2p_service import P2PService 
from core.p2p.payloads.version_payload import VersionPayload
from core.p2p.payloads.block_payload import BlockPayload
from core.p2p.payloads.tx_payload import TxPayload
from core.p2p.payloads.get_headers_payload import GetHeadersPayload
from core.p2p.payloads.headers_payload import HeadersPayload
from core.p2p.payloads.inv_payload import InvPayload
from core.p2p.payloads.get_data_payload import GetDataPayload
from core.p2p.payloads.inv_vector import InvVector
from core.serializers.block_serializer import BlockSerializer 
from core.serializers.block_header_serializer import BlockHeaderSerializer
from core.deserializers.block_deserializer import BlockDeserializer
from core.deserializers.transaction_deserializer import TransactionDeserializer
from core.validators.header_chain_validator import HeaderChainValidator


class FullNode(INode, IBlockValidatorRole):

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool,
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None):
        
        self._blockchain = blockchain
        self._consensus_manager = consensus_manager
        self._public_key_map = public_key_map
        self._mempool = mempool
        self._p2p_service = P2PService(self, host, port, seed_peers) 
        
        logging.info('Full Node (Auditor Jefe) inicializado.')

    async def start(self): 
        logging.info('Full Node iniciando servicios P2P...')
        await self._p2p_service.start_service()
        logging.info('Full Node iniciado y listo.')

    async def stop(self) -> None:
        logging.info('Full Node deteniendo servicios P2P...')
        await self._p2p_service.stop_service()
        logging.info('Full Node detenido.')

    def handle_message(self, message: Message, peer_id: str) -> None: 
        command = message.command
        payload = message.payload 
        peer = self._p2p_service.get_peer(peer_id)
        if not peer:
            logging.warning(f"P2P: Mensaje de 'peer' desconocido {peer_id}. Descartando.")
            return

        try:
            if command == 'version' and isinstance(payload, VersionPayload):
                self._handle_version_handshake(payload, peer)
                
            elif command == 'getheaders' and isinstance(payload, GetHeadersPayload):
                self._handle_get_headers(payload, peer)
                
            elif command == 'headers' and isinstance(payload, HeadersPayload):
                self._handle_headers(payload, peer)
            
            elif command == 'inv' and isinstance(payload, InvPayload):
                self._handle_inv(payload, peer)
                
            elif command == 'getdata' and isinstance(payload, GetDataPayload):
                self._handle_get_data(payload, peer)
            
            elif command == 'block' and isinstance(payload, BlockPayload):
                block_obj = BlockDeserializer.from_dict(payload.block_data)
                self.validate_block_rules(block_obj)
                
            elif command == 'tx' and isinstance(payload, TxPayload):
                tx_obj = TransactionDeserializer.from_dict(payload.tx_data)
                self.validate_tx_rules(tx_obj)
                
        except (ValueError, TypeError) as e:
            logging.warning(f"Error P2P: Payload inválido de {peer_id} para '{command}'. {e}")

    # --- Métodos Helper (con Docstrings Corregidos) ---

    def _get_current_height(self) -> int:
        '''Obtiene el índice (altura) del último bloque.'''
        if not self._blockchain.chain: return -1
        return self._blockchain.chain[-1].index
        
    def _get_block_by_index(self, index: int) -> Block | None:
        '''Obtiene un bloque por su índice (posición) en la cadena.'''
        if index < 0 or index >= len(self._blockchain.chain): return None
        return self._blockchain.chain[index]
        
    def _get_block_hash_by_index(self, index: int) -> str | None:
        '''Obtiene solo el hash de un bloque usando su índice.'''
        block = self._get_block_by_index(index)
        return block.hash if block else None
        
    def _get_block_by_hash(self, block_hash: str) -> Block | None:
        '''Obtiene un objeto Bloque completo buscando por su hash.'''
        # (Optimización: Deberías usar un dict 'hash -> index' en Blockchain)
        for block in reversed(self._blockchain.chain):
            if block.hash == block_hash: return block
        return None
        
    def _have_block(self, block_hash: str) -> bool:
        '''Verifica (True/False) si un bloque ya existe en la cadena.'''
        return self._get_block_by_hash(block_hash) is not None

    # --- Handlers de Sincronización P2P ---

    def initiate_handshake(self, peer: Peer): 
        my_height = self._get_current_height()
        version_payload = VersionPayload(
            protocol_version = 1, 
            services = 0, 
            timestamp = int(time.time()), 
            best_height = my_height
        )
        asyncio.create_task(
            self._p2p_service.send_message(peer, 'version', version_payload)
        )

    def _handle_version_handshake(self, payload: VersionPayload, peer: Peer):
        my_height = self._get_current_height()
        if payload.best_height > my_height:
            logging.info(f'Sincronización: El par {peer.host} tiene {payload.best_height} (nosotros {my_height}). Pidiendo headers.')
            self._send_get_headers(peer)
            
    def _send_get_headers(self, peer: Peer):
        genesis_hash = self._get_block_hash_by_index(0)
        locator_hashes = [genesis_hash] if genesis_hash else []
        
        get_headers_payload = GetHeadersPayload(
            protocol_version = 1, 
            locator_hashes = locator_hashes, 
            hash_stop = '0' * 64
        )
        asyncio.create_task(
            self._p2p_service.send_message(peer, 'getheaders', get_headers_payload)
        )

    def _handle_get_headers(self, payload: GetHeadersPayload, peer: Peer):
        
        current_height = self._get_current_height()
        start_index = max(0, current_height - 10) # (Lógica simple)
        
        headers_to_send: List[Dict[str, Any]] = []
        for i in range(start_index, current_height + 1):
            block = self._get_block_by_index(i)
            if block:
                headers_to_send.append(BlockHeaderSerializer.to_dict(block))
                
        if headers_to_send:
            headers_payload = HeadersPayload(headers=headers_to_send)
            asyncio.create_task(
                self._p2p_service.send_message(peer, 'headers', headers_payload)
            )
            
    def _handle_headers(self, payload: HeadersPayload, peer: Peer):
        
        if not payload.headers:
            logging.info(f'Sincronización: {peer.host} envió 0 headers.')
            return
        
        first_header_prev_hash = payload.headers[0].get('previous_hash')

        if not first_header_prev_hash:
             logging.warning(f'P2P: {peer.host} envió un primer header malformado (sin prev_hash).')
             return

        anchor_block = self._get_block_by_hash(first_header_prev_hash)
        
        if not anchor_block:
            logging.warning(f'P2P: {peer.host} envió headers huérfanos (no encontramos el ancla {first_header_prev_hash[:6]}).')
            return
        
        is_valid_chain = HeaderChainValidator.verify(
            headers=payload.headers,
            last_known_block_hash=anchor_block.hash,
            last_known_block_timestamp=anchor_block.timestamp
        )

        if not is_valid_chain:
            logging.warning(f'P2P: {peer.host} envió una cadena de headers inválida. Descartando.')
            return
        
        items_to_request: List[InvVector] = []
        new_headers_found: int = 0

        for header_dict in payload.headers:
            
            block_hash = header_dict.get('hash')
            if not block_hash:
                logging.warning(f"P2P: {peer.host} envió un header sin hash. Ignorando item.")
                continue # Saltar este header corrupto

            if not self._have_block(block_hash):
                new_headers_found += 1
                inv_vector = InvVector(type=2, hash=block_hash)
                items_to_request.append(inv_vector)

        if items_to_request:
            logging.info(f'Sincronización: Headers de {peer.host} válidos. {new_headers_found} son nuevos. Pidiendo bloques...')
            get_data_payload = GetDataPayload(inventory=items_to_request)
            asyncio.create_task(
                self._p2p_service.send_message(peer, 'getdata', get_data_payload)
            )
            
        elif payload.headers:
             logging.info(f'Sincronización: {peer.host} envió {len(payload.headers)} headers, pero ya los teníamos todos. Sincronizados.')

    # --- Handlers de Gossip (Anuncios y Datos) ---

    def _handle_inv(self, payload: InvPayload, peer: Peer):
        
        items_to_request: List[InvVector] = []
        
        for item in payload.inventory:
            
            if item.type == 2 and not self._have_block(item.hash):
                items_to_request.append(item)

            elif item.type == 1 and not self._mempool.have_transaction(item.hash):
                items_to_request.append(item)
                
        if items_to_request:
            get_data_payload = GetDataPayload(inventory=items_to_request)
            asyncio.create_task(
                self._p2p_service.send_message(peer, 'getdata', get_data_payload)
            )
    
    def _handle_get_data(self, payload: GetDataPayload, peer: Peer):
        
        for item in payload.inventory:
            
            if item.type == 2:
                block = self._get_block_by_hash(item.hash)
                if block:
                    block_payload = BlockPayload(block_data = BlockSerializer.to_dict(block))
                    asyncio.create_task(self._p2p_service.send_message(peer, 'block', block_payload))
                    
            elif item.type == 1:
                
                tx = self._mempool.get_transaction(item.hash)
                
                if tx:
                    tx_payload = TxPayload(tx_data = TransactionSerializer.to_dict(tx))
                    asyncio.create_task(self._p2p_service.send_message(peer, 'tx', tx_payload))
                    
    def _broadcast_new_block(self, block: Block):
        inv_vector = InvVector(type = 2, hash = block.hash)
        inv_payload = InvPayload(inventory = [inv_vector])
        asyncio.create_task(self._p2p_service.broadcast('inv', inv_payload))

    def _broadcast_new_tx(self, tx: Transaction):
        inv_vector = InvVector(type=1, hash=tx.tx_hash)
        inv_payload = InvPayload(inventory=[inv_vector])
        asyncio.create_task(self._p2p_service.broadcast('inv', inv_payload))

    # --- Implementación de Roles (IBlockValidatorRole) ---

    def validate_block_rules(self, block: Block) -> bool:
        
        is_new_block = self._consensus_manager.add_block(block, self._public_key_map)
        
        if is_new_block:
            logging.info(f"Bloque {block.index} (hash: {block.hash[:6]}) aceptado.")
            self._broadcast_new_block(block)
            self._mempool.remove_mined_transactions(block.data)
            
        return is_new_block

    def validate_tx_rules(self, tx: Transaction) -> bool:

        if not TransactionValidator.verify(tx):
            logging.warning(f"TX {tx.tx_hash} rechazada (P2P): Integridad fallida.")
            return False
            
        if tx.signature is not None:
            if not tx.entries: return False
            owner_id = tx.entries[0].source_id
            public_key = self._public_key_map.get(owner_id)
            
            if not public_key or not TransactionVerifier.verify(public_key, tx.tx_hash, tx.signature):
                logging.warning(f"TX {tx.tx_hash} rechazada (P2P): Firma inválida.")
                return False
        
        is_new_tx = self._mempool.add_transaction(tx)
        
        if is_new_tx:
            logging.info(f"TX {tx.tx_hash[:6]} aceptada en Mempool.")
            self._broadcast_new_tx(tx)

        return is_new_tx