# network_of_interactive_nodes/core/deserializers/blockchain_deserializer.py
'''
class BlockchainDeserializer:
    Contiene la lógica pura para deserializar un dict a un objeto Blockchain.

    Methods:
        from_dict(data: dict) -> Blockchain:
            1. Crear una nueva instancia vacía de Blockchain.
            2. Extraer la lista de diccionarios de bloques.
            3. Iterar sobre la lista de diccionarios.
            4. Deserializar cada bloque.
            5. Añadir el bloque reconstruido a la cadena.
            6. Retornar el objeto Blockchain reconstruido.
'''

from typing import Any, List, Dict

# Importaciones de la arquitectura
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.deserializers.block_deserializer import BlockDeserializer

class BlockchainDeserializer:

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Blockchain:
        
        try:
            new_blockchain = Blockchain()

            blocks_data_list: List[Dict[str, Any]] = data['chain']

            for block_data in blocks_data_list:
                reconstructed_block: Block = BlockDeserializer.from_dict(block_data)
                new_blockchain.add_block_forced(reconstructed_block)
            
            return new_blockchain

        except (KeyError, ValueError, TypeError) as e:
            raise ValueError(f'Dato corrupto o malformado en Blockchain JSON ({e})')