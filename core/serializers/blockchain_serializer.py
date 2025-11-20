# network_of_interactive_nodes/core/serializers/blockchain_serializer.py
'''
class BlockchainSerializer:
    Contiene la lógica pura para serializar un objeto Blockchain a un diccionario.

    Methods:
        to_dict(blockchain: Blockchain) -> dict[str, Any]:
            1. Obtener la lista de bloques (la 'cadena') del objeto Blockchain.
            2. Serializar la lista de Bloques.
            3. Ensamblar el diccionario final (con 'chain' como clave).
            4. Retornar el diccionario.
'''

from typing import Any, List, Dict

# Importaciones de la arquitectura
from core.models.blockchain import Blockchain
from core.serializers.block_serializer import BlockSerializer

class BlockchainSerializer:
    @staticmethod
    def to_dict(blockchain: Blockchain) -> Dict[str, Any]:
        block_list = blockchain.chain 
        
        serialized_blocks: List[Dict[str, Any]] = [
            BlockSerializer.to_dict(block) for block in block_list
        ]

        blockchain_dict: Dict[str, Any] = {
            'chain': serialized_blocks
        }

        return blockchain_dict