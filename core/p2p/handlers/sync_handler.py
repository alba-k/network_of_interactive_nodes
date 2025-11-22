# core/p2p/handlers/sync_handler.py
'''
class SyncHandler:
    Estrategia (Handler) especializada en la Sincronización y Handshake.
    
    Responsabilidad:
        Manejar los mensajes de protocolo: 'version', 'getheaders', 'headers'.
        Se encarga de negociar la conexión inicial y de solicitar cabeceras 
        para mantener la cadena local actualizada.

    Attributes:
        _blockchain (Blockchain): Referencia al estado para consultar altura/hashes.
        _p2p_service (P2PService): Transporte para enviar respuestas.

    Methods:
        initiate_handshake(peer): Envía el mensaje 'version' inicial.
        
        handle_version(payload, peer): Procesa el handshake y decide si pedir headers.
        
        handle_get_headers(payload, peer): Responde a una petición de headers.
        
        handle_headers(payload, peer): 
            1. Valida una cadena de headers recibida (HeaderChainValidator).
            2. Si es válida y nueva, solicita los bloques completos ('getdata').
'''

import logging
import time
import asyncio
from typing import Dict, List, Any

# --- Importaciones de Modelos y Estado ---
from core.models.blockchain import Blockchain
from core.models.block import Block

# --- Importaciones de P2P ---
from core.p2p.p2p_service import P2PService
from core.p2p.peer import Peer
from core.p2p.payloads.version_payload import VersionPayload
from core.p2p.payloads.get_headers_payload import GetHeadersPayload
from core.p2p.payloads.headers_payload import HeadersPayload
from core.p2p.payloads.get_data_payload import GetDataPayload
from core.p2p.payloads.inv_vector import InvVector

# --- Importaciones del Núcleo Estático ---
from core.serializers.block_header_serializer import BlockHeaderSerializer
from core.validators.header_chain_validator import HeaderChainValidator


class SyncHandler:

    def __init__(self, blockchain: Blockchain, p2p_service: P2PService):
        # Dependencia OBLIGATORIA: No se puede sincronizar sin una cadena (o stub)
        self._blockchain = blockchain
        self._p2p_service = p2p_service
        logging.info("SyncHandler (Servicio de Sincronización) inicializado.")

    # --- Métodos Públicos (Acciones de Inicio) ---

    def initiate_handshake(self, peer: Peer) -> None:
        '''Inicia la conexión enviando nuestra 'version'.'''
        my_height = self._get_current_height()
        
        version_payload = VersionPayload(
            protocol_version = 1, 
            services = 1, # 1 = NODE_NETWORK (Full Node)
            timestamp = int(time.time()), 
            best_height = my_height
        )
        
        asyncio.create_task(
            self._p2p_service.send_message(peer, 'version', version_payload)
        )

    # --- Handlers de Mensajes ---

    def handle_version(self, payload: VersionPayload, peer: Peer) -> None:
        '''Responde al handshake de un par.'''
        # 1. Compara alturas.
        my_height = self._get_current_height()
        
        # 2. Si el par tiene más bloques, iniciamos descarga (Headers First).
        if payload.best_height > my_height:
            logging.info(f'Sync: El par {peer.host} nos gana por {payload.best_height - my_height} bloques. Pidiendo headers...')
            self._send_get_headers(peer)

    def handle_get_headers(self, payload: GetHeadersPayload, peer: Peer) -> None:
        '''Otro nodo nos pide headers para sincronizarse.'''
        # 1. Calcular rango (Lógica simple: últimos 2000 o menos).
        current_height = self._get_current_height()
        start_index = max(0, current_height - 10) # (Simplificado para demo)
        
        headers_to_send: List[Dict[str, Any]] = []
        
        # 2. Buscar y serializar headers.
        for i in range(start_index, current_height + 1):
            block = self._get_block_by_index(i)
            if block:
                headers_to_send.append(BlockHeaderSerializer.to_dict(block))
                
        # 3. Enviar respuesta.
        if headers_to_send:
            headers_payload = HeadersPayload(headers=headers_to_send)
            asyncio.create_task(
                self._p2p_service.send_message(peer, 'headers', headers_payload)
            )

    def handle_headers(self, payload: HeadersPayload, peer: Peer) -> None:
        '''Recibimos headers de la red. Validar y decidir si pedir bloques.'''
        if not payload.headers: return
        
        # 1. Validar el punto de enlace (Ancla).
        first_header = payload.headers[0]
        prev_hash = first_header.get('previous_hash')
        
        if not prev_hash: return 

        anchor_block = self._get_block_by_hash(prev_hash)
        if not anchor_block:
            # En producción, aquí pediríamos el padre recursivamente.
            logging.warning(f'Sync: Headers huérfanos de {peer.host}.')
            return
        
        # 2. Validar la cadena de headers (PoW rápido).
        is_valid = HeaderChainValidator.verify(
            headers=payload.headers,
            last_known_block_hash=anchor_block.hash,
            last_known_block_timestamp=anchor_block.timestamp
        )

        if not is_valid:
            logging.warning(f'Sync: Cadena de headers inválida de {peer.host}.')
            return
        
        # 3. Filtrar lo que ya tenemos.
        items_to_request: List[InvVector] = []
        
        for header in payload.headers:
            b_hash = header.get('hash')
            if b_hash and not self._have_block(b_hash):
                # Tipo 2 = Bloque
                items_to_request.append(InvVector(type=2, hash=b_hash))

        # 4. Pedir los bloques completos (GetData).
        if items_to_request:
            logging.info(f'Sync: Headers válidos. Solicitando {len(items_to_request)} bloques completos.')
            get_data = GetDataPayload(inventory=items_to_request)
            asyncio.create_task(
                self._p2p_service.send_message(peer, 'getdata', get_data)
            )

    # --- Helpers Internos (Acceso a Blockchain) ---

    def _send_get_headers(self, peer: Peer):
        genesis = self._get_block_by_index(0)
        locator = [genesis.hash] if genesis else []
        payload = GetHeadersPayload(1, locator, '0'*64)
        asyncio.create_task(self._p2p_service.send_message(peer, 'getheaders', payload))

    def _get_current_height(self) -> int:
        if not self._blockchain.chain: return -1
        return self._blockchain.chain[-1].index

    def _get_block_by_index(self, index: int) -> Block | None:
        if index < 0 or index >= len(self._blockchain.chain): return None
        return self._blockchain.chain[index]

    def _get_block_by_hash(self, b_hash: str) -> Block | None:
        # Búsqueda lineal (En producción usar índice)
        for b in reversed(self._blockchain.chain):
            if b.hash == b_hash: return b
        return None

    def _have_block(self, b_hash: str) -> bool:
        return self._get_block_by_hash(b_hash) is not None