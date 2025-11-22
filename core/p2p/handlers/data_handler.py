# core/p2p/handlers/data_handler.py
'''
class DataHandler:
    Estrategia (Handler) especializada en servir datos a otros pares.
    
    Responsabilidad:
        Manejar mensajes 'getdata'. Busca los items solicitados (Bloques o TXs)
        en el almacenamiento local (Blockchain/Mempool) y los envía al par solicitante.

    Attributes:
        _blockchain (Blockchain): Referencia al estado de la cadena.
        _mempool (Mempool): Referencia al pool de transacciones.
        _p2p_service (P2PService): Servicio de transporte para enviar las respuestas.

    Methods:
        handle_get_data(payload: GetDataPayload, peer: Peer) -> None:
            1. Itera sobre el inventario solicitado.
            2. Si piden Bloque (Type 2): Lo busca, serializa y envía mensaje 'block'.
            3. Si piden TX (Type 1): La busca, serializa y envía mensaje 'tx'.
'''

import logging
import asyncio

# --- Importaciones de Modelos y Estado ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool

# --- Importaciones de P2P ---
from core.p2p.p2p_service import P2PService
from core.p2p.peer import Peer
from core.p2p.payloads.get_data_payload import GetDataPayload
from core.p2p.payloads.block_payload import BlockPayload
from core.p2p.payloads.tx_payload import TxPayload

# --- Importaciones de Serializadores (Núcleo Estático) ---
from core.serializers.block_serializer import BlockSerializer
from core.serializers.transaction_serializer import TransactionSerializer

class DataHandler:

    def __init__(self, 
                 blockchain: Blockchain, 
                 mempool: Mempool, 
                 p2p_service: P2PService):
        
        # Dependencias OBLIGATORIAS (Sin datos no hay handler)
        self._blockchain = blockchain
        self._mempool = mempool
        self._p2p_service = p2p_service
        
        logging.info("DataHandler (Servicio de Datos) inicializado.")

    def handle_get_data(self, payload: GetDataPayload, peer: Peer) -> None:
        '''
        Procesa una solicitud 'getdata' y responde con los objetos encontrados.
        '''
        
        # 1. Iterar sobre cada item solicitado en el inventario del payload.
        for item in payload.inventory:
            
            # ---------------------------------------------------------
            # CASO A: Solicitud de BLOQUE (Type = 2)
            # ---------------------------------------------------------
            if item.type == 2:
                # 2. Buscar el bloque por su hash en la cadena local.
                block = self._find_block_by_hash(item.hash)
                
                if block:
                    # 3. Si existe, serializarlo a DTO.
                    block_dict = BlockSerializer.to_dict(block)
                    block_payload = BlockPayload(block_data=block_dict)
                    
                    # 4. Enviar el mensaje 'block' al par solicitante.
                    asyncio.create_task(
                        self._p2p_service.send_message(peer, 'block', block_payload)
                    )
            
            # ---------------------------------------------------------
            # CASO B: Solicitud de TRANSACCIÓN (Type = 1)
            # ---------------------------------------------------------
            elif item.type == 1:
                # 5. Buscar la transacción por su hash en el Mempool.
                tx = self._mempool.get_transaction(item.hash)
                
                if tx:
                    # 6. Si existe, serializarla a DTO.
                    tx_dict = TransactionSerializer.to_dict(tx)
                    tx_payload = TxPayload(tx_data=tx_dict)
                    
                    # 7. Enviar el mensaje 'tx' al par solicitante.
                    asyncio.create_task(
                        self._p2p_service.send_message(peer, 'tx', tx_payload)
                    )

    # --- Método Helper Privado ---

    def _find_block_by_hash(self, block_hash: str):
        '''Helper interno para buscar en la blockchain lineal.'''
        for block in reversed(self._blockchain.chain):
            if block.hash == block_hash:
                return block
        return None