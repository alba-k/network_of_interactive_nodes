# network_of_interactive_nodes/core/serializers/block_serializer.py
'''
class BlockSerializer:
    Contiene la lógica pura para serializar un Block a un diccionario.

    Methods:
        to_dict(block: Block) -> dict[str, Any]: Convierte un Block a un dict.
            1. Serializar la lista de Transacciones.
            2. Ensamblar el diccionario final del bloque.
            3. Retornar el diccionario.
'''

from typing import Any, List, Dict
from core.models.block import Block
from core.serializers.transaction_serializer import TransactionSerializer

class BlockSerializer:
    @staticmethod
    def to_dict(block: Block) -> Dict[str, Any]:
        serialized_transactions: List[Dict[str, Any]] = [
            TransactionSerializer.to_dict(tx) for tx in block.data
        ]

        block_dict: Dict[str, Any] = {
            'index': block.index,
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'bits': block.bits,
            'merkle_root': block.merkle_root,
            'data': serialized_transactions,
            'nonce': block.nonce,
            'hash': block.hash,
            'mining_time': block.mining_time
        }
        
        return block_dict