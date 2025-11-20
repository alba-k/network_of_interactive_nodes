# network_of_interactive_nodes/core/managers/p2p_manager.py
'''
class P2PManager(INode):
    Implementa el "Rol" de Red P2P (el "chisme" o "gossip").
    Se encarga *solo* de la lógica de red (asyncio) y la comunicación con los 'peers'.

    Attributes:
        _validator_role (IBlockValidatorRole): Gestor de Consenso (Inyectado) al que se le entregan los bloques y TXs recibidos.
        _p2p_service    (P2PService):          La capa de transporte (asyncio) que maneja los sockets (Compuesto).
        _blockchain     (Blockchain):          Referencia a la cadena para responder a 'getheaders' y 'getdata'.
        _mempool        (Mempool):             Referencia al mempool para responder a 'getdata'.

    Methods:
        start(self) -> None: (Implementa INode) Inicia los servicios P2P.
            1. Llama (await) a self._p2p_service.start_service().

        stop(self) -> None: (Implementa INode) Detiene los servicios P2P.
            1. Llama (await) a self._p2p_service.stop_service().

        handle_message(self, message: Message, peer_id: str) -> None: (Router / INode) Punto de entrada principal (callback) para mensajes recibidos de P2PService.
            1. Obtiene el 'command' y 'payload' del DTO Message.
            2. Verifica que el 'peer_id' es válido (usando _p2p_service.get_peer).
            3. Enruta (router) el 'payload' al método _handle_... correcto según el 'command'.
            4. Para 'block' y 'tx', llama a los 'handlers' especializados (_handle_block, _handle_tx) que manejan la delegación.

        initiate_handshake(self, peer: Peer) -> None: (Acción / INode) Inicia el "apretón de manos" (handshake) con un par recién conectado.
            1. Obtiene la altura actual de la blockchain local (_get_current_height).
            2. Crea el DTO 'VersionPayload' (archivo #37) con la altura y timestamp.
            3. Envía el mensaje 'version' al 'peer' (usando _p2p_service.send_message).

        broadcast_new_block(self, block: Block) -> None: (Acción P2P / "Chisme") Anuncia un bloque nuevo a todos los pares conectados.  
            1. Crea un 'InvVector' (archivo #35) (type=2, hash=block.hash).
            2. Envuelve el vector en un 'InvPayload'.
            3. Llama a self._p2p_service.broadcast('inv', ...).

        broadcast_new_tx(self, tx: Transaction) -> None: (Acción P2P / "Chisme") Anuncia una TX nueva a todos los pares conectados.
            1. Crea un 'InvVector' (type=1, hash=tx.tx_hash).
            2. Envuelve el vector en un 'InvPayload'.
            3. Llama a self._p2p_service.broadcast('inv', ...).

        _handle_block(self, payload: BlockPayload, peer_id: str) -> None: (Handler) Procesa un 'block' completo recibido de un par.
            1. (Red): Deserializa el 'dict' del payload (Delega a BlockDeserializer).
            2. (Consenso): Delega la validación al 'validator_role' (llama a IBlockValidatorRole.validate_block_rules).
            3. (Red): Si el consenso (Paso 2) retorna True (bloque aceptado), llama a broadcast_new_block (inicia el "chisme").

        _handle_tx(self, payload: TxPayload, peer_id: str) -> None: (Handler) Procesa una 'tx' completa recibida de un par.
            1. (Red): Deserializa el 'dict' del payload (Delega a TransactionDeserializer).
            2. (Consenso): Delega la validación al 'validator_role' (llama a IBlockValidatorRole.validate_tx_rules).
            3. (Red): Si el consenso (Paso 2) retorna True (TX aceptada), llama a broadcast_new_tx (inicia el "chisme").

        _handle_version_handshake(self, payload: VersionPayload, peer: Peer) -> None: (Handler) Procesa un mensaje 'version' de un par.
            1. Compara la altura del 'payload' (payload.best_height) con la local (_get_current_height).
            2. Si el par está más adelantado (best_height > my_height), llama a _send_get_headers (inicia sincronización).

         _handle_headers(self, payload: HeadersPayload, peer: Peer) -> None: (Handler) Procesa una lista de 'headers' recibida de un par.
            1. Obtiene el "ancla" (último hash/timestamp conocido) de la blockchain local.
            2. Delega la validación de la cadena (Llama a HeaderChainValidator.verify).
            3. Si es inválida, descarta.
            4. Si es válida, filtra los 'headers' que no tiene (`_have_block`).
            5. Si hay 'headers' nuevos, crea 'InvVector' (type=2) para ellos.
            6. Envía un mensaje 'getdata' para pedir los bloques completos faltantes.
 
        _handle_inv(self, payload: InvPayload, peer: Peer) -> None: (Handler) Procesa un 'inv' (anuncio / "chisme") de un par.
            1. Itera sobre el 'inventory' del payload.
            2. Filtra los 'hashes' de bloques (type=2) y TXs (type=1) que no tiene (usando _have_block y _mempool.have_transaction).
            3. Si hay items nuevos, agrupa los 'InvVector' y envía un mensaje 'getdata' para pedirlos.

         _handle_get_data(self, payload: GetDataPayload, peer: Peer) -> None: (Handler) Procesa un 'getdata' (petición de datos) de un par.
            1. Itera sobre el 'inventory' del payload.
            2. Si piden un Bloque (type=2), lo busca en la `_blockchain` (_get_block_by_hash).
            3. Si lo encuentra, lo serializa (BlockSerializer.to_dict) y lo envía (mensaje 'block').
            4. Si piden una TX (type=1), la busca en el `_mempool` (_mempool.get_transaction).
            5. Si la encuentra, la serializa (TransactionSerializer.to_dict) y la envía (mensaje 'tx').
        
        _send_get_headers(self, peer: Peer) -> None: (Acción Interna) Envía un mensaje 'getheaders' a un par para iniciar sincronización.
            1. Obtiene el hash del bloque Génesis (índice 0) para usarlo como "locator".
            2. Crea el DTO 'GetHeadersPayload' con el locator y hash_stop en cero.
            3. Envía el mensaje 'getheaders' al par.

        _get_current_height(self) -> int: (Helper) Obtiene el índice (altura) del último bloque de la cadena local.
            1. Verifica si la cadena está vacía (retorna -1).
            2. Retorna el atributo '.index' del último bloque en la lista '_chain'.

        _get_block_by_index(self, index: int) -> Block | None: (Helper) Obtiene un bloque por su índice (posición) en la cadena.
            1. Valida que el índice esté dentro del rango de la lista.
            2. Retorna el bloque correspondiente o None si no existe.

        _get_block_hash_by_index(self, index: int) -> str | None: (Helper) Obtiene solo el hash de un bloque usando su índice.
            1. Llama a _get_block_by_index.
            2. Si existe el bloque, retorna su '.hash', si no, retorna None.

        _get_block_by_hash(self, block_hash: str) -> Block | None: (Helper) Busca un objeto Bloque completo por su hash.
            1. Recorre la cadena (idealmente en reverso) buscando coincidencia de hash.
            2. Retorna el bloque encontrado o None.

        _have_block(self, block_hash: str) -> bool: (Helper) Verifica si un bloque ya existe en la cadena local.
            1. Llama a _get_block_by_hash.
            2. Retorna True si el resultado no es None.    
'''

import logging
import time
import asyncio 
from typing import Dict, List, Tuple, Any, Optional

# Importaciones de Interfaces (Contratos) 
from core.interfaces.i_node import INode 
from core.interfaces.i_node_roles import IBlockValidatorRole

# Importaciones de Gestores y Modelos (Estado) 
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.models.transaction import Transaction
from core.mempool.mempool import Mempool

# Importaciones del Núcleo Estático (Herramientas) 
from core.serializers.transaction_serializer import TransactionSerializer
from core.serializers.block_serializer import BlockSerializer 
from core.serializers.block_header_serializer import BlockHeaderSerializer
from core.deserializers.block_deserializer import BlockDeserializer
from core.deserializers.transaction_deserializer import TransactionDeserializer
from core.validators.header_chain_validator import HeaderChainValidator

# Importaciones de P2P (DTOs y Servicios) 
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


class P2PManager(INode):

    def __init__(self, 
                 validator_role: IBlockValidatorRole,
                 blockchain: Blockchain,
                 mempool: Mempool,
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None):
        
        # Inyección de Dependencias (Gestores y Estado) 
        self._validator_role = validator_role
        self._blockchain = blockchain
        self._mempool = mempool
        
        # Composición (Este Gestor "posee" el P2PService) 
        self._p2p_service = P2PService(self, host, port, seed_peers) 
        
        logging.info('P2P Manager (Gestor de Red) inicializado.')

    # Implementación de INode (Contrato) 

    async def start(self): 
        logging.info('P2P Manager iniciando servicios P2P...')
        await self._p2p_service.start_service()
        logging.info('P2P Manager iniciado y listo.')

    async def stop(self) -> None:
        logging.info('P2P Manager deteniendo servicios P2P...')
        await self._p2p_service.stop_service()
        logging.info('P2P Manager detenido.')

    def handle_message(self, message: Message, peer_id: str) -> None: 
        command = message.command
        payload = message.payload 
        peer = self._p2p_service.get_peer(peer_id)
        if not peer:
            logging.warning(f'''P2P: Mensaje de 'peer' desconocido {peer_id}. Descartando.''')
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
                self._handle_block(payload, peer_id) # Delegar al handler de bloque

            elif command == 'tx' and isinstance(payload, TxPayload):
                self._handle_tx(payload, peer_id) # Delegar al handler de TX
                
        except (ValueError, TypeError) as e:
            logging.warning(f'''Error P2P: Payload inválido de {peer_id} para '{command}'. {e}''')

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

    # Métodos Helper (Acceso al Estado Inyectado) 

    def _get_current_height(self) -> int:
        if not self._blockchain.chain: return -1
        return self._blockchain.chain[-1].index
        
    def _get_block_by_index(self, index: int) -> Block | None:
        if index < 0 or index >= len(self._blockchain.chain): return None
        return self._blockchain.chain[index]
        
    def _get_block_hash_by_index(self, index: int) -> str | None:
        block = self._get_block_by_index(index)
        return block.hash if block else None
        
    def _get_block_by_hash(self, block_hash: str) -> Block | None:
        for block in reversed(self._blockchain.chain):
            if block.hash == block_hash: return block
        return None
        
    def _have_block(self, block_hash: str) -> bool:
        return self._get_block_by_hash(block_hash) is not None

    # Handlers de Sincronización P2P (Lógica Pura de Red) 

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
        start_index = max(0, current_height - 10) 
        
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
                continue 

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

    # Handlers de "Chisme" (Gossip) (Acciones P2P) 

    def broadcast_new_block(self, block: Block):
        inv_vector = InvVector(type = 2, hash = block.hash)
        inv_payload = InvPayload(inventory = [inv_vector])
        asyncio.create_task(self._p2p_service.broadcast('inv', inv_payload))

    def broadcast_new_tx(self, tx: Transaction):
        inv_vector = InvVector(type=1, hash=tx.tx_hash)
        inv_payload = InvPayload(inventory=[inv_vector])
        asyncio.create_task(self._p2p_service.broadcast('inv', inv_payload))

    # Handlers de Consenso (Delegación) 

    def _handle_block(self, payload: BlockPayload, peer_id: str):
    
        try:
            block_obj = BlockDeserializer.from_dict(payload.block_data)
            is_new_block = self._validator_role.validate_block_rules(block_obj)
            
            if is_new_block:
                self.broadcast_new_block(block_obj)
        
        except (ValueError, TypeError) as e:
            logging.warning(f'''P2P: {peer_id} envió un bloque inválido (Deserialización falló). {e}''')

    def _handle_tx(self, payload: TxPayload, peer_id: str):

        try:
            tx_obj = TransactionDeserializer.from_dict(payload.tx_data)
            is_new_tx = self._validator_role.validate_tx_rules(tx_obj)
            
            if is_new_tx:
                self.broadcast_new_tx(tx_obj)
        
        except (ValueError, TypeError) as e:
            logging.warning(f"P2P: {peer_id} envió una TX inválida (Deserialización falló). {e}")