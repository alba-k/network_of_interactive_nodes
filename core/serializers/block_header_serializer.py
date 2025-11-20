# network_of_interactive_nodes/core/serializers/block_header_serializer.py
'''
class BlockHeaderSerializer:
    Contiene la lógica pura para serializar un "Header" (un Block sin transacciones) a un diccionario.
    
    Methods:
        to_dict(block: Block) -> Dict[str, Any]: Serializa el header del bloque.
            1. Crear un diccionario (dict) con todos los campos del bloque.
            2. Omitir el campo 'data' (transacciones).
            3. Retornar el diccionario (header).
'''

from typing import Any, Dict
from core.models.block import Block

class BlockHeaderSerializer:
    @staticmethod
    def to_dict(block: Block) -> Dict[str, Any]:
        header_dict: Dict[str, Any] = {
            'index': block.index,
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'bits': block.bits,
            'merkle_root': block.merkle_root,
            'nonce': block.nonce,
            'hash': block.hash
        }
        return header_dict