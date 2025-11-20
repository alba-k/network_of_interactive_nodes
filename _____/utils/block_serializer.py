# block_serializer.py 
'''
class BlockSerializer:   
    Especialista en (des)serialización de bloques.
    Convierte objetos (Block, Blockchain) a/desde diccionarios (JSON).

    Attributes:

    Methods:
        to_dict(block)->                    Dict:           Convierte un objeto Block a un diccionario.
        from_dict(data)->                   Block:          Convierte un dict a Block, verificando integridad.
        blockchain_to_dict_list(bc)->       List[Dict]:     Convierte un Blockchain a lista de dicts.
        blockchain_from_dict_list(data)->   Blockchain:     Convierte lista de dicts a un Blockchain.
'''

from core.models.block import Block # Importa la clase de estado 'Block'
from core.utils.crypto_utils import CryptoUtils # Importa la 'calculadora' criptográfica
from core.models.blockchain import Blockchain # Importa el contenedor 'Blockchain'
from typing import Dict, Any, List # Importaciones para type hints
from dataclasses import asdict # Herramienta para convertir dataclass a dict
from core.models.transaction import Transaction # Importa la clase 'Transaction' (para la lista 'data')

class BlockSerializer:

    @staticmethod
    def to_dict(block: Block) -> Dict[str, Any]:
        '''
        Convierte un objeto Block (y sus Transacciones) a un diccionario.
        '''

        # --- Serializar la lista de Transacciones ---
        data_as_dicts: List[Dict[str, Any]] = [asdict(tx) for tx in block.data]

        block_dict: Dict[str, Any] = {
            'index': block.index,
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'hash': block.hash,
            'nonce': block.nonce,
            'difficulty': block.difficulty,
            'merkle_root': block.merkle_root,
            'data': data_as_dicts,
        }

        return block_dict 

    @staticmethod
    def from_dict(block_data: Dict[str, Any]) -> Block:
        '''
        Convierte un diccionario a un objeto Block Y VERIFICA SU INTEGRIDAD
        '''
        try:
            # 1. --- Recalcular el hash ---
            calculated_hash: str = CryptoUtils.calculate_hash(
                index = block_data['index'],
                timestamp = block_data['timestamp'],
                previous_hash = block_data['previous_hash'],
                merkle_root = block_data['merkle_root'],
                difficulty = block_data['difficulty'],
                nonce = block_data['nonce']
            )
            
            stored_hash: str = block_data['hash']

            # 2. --- VERIFICACIÓN DE SEGURIDAD ---
            if calculated_hash != stored_hash:
                raise ValueError(f"Hash corrupto para bloque #{block_data['index']}.")
            
            # 3. --- Recrear los objetos Transaction ---
            data_objects: List[Transaction] = [Transaction(**tx_data) for tx_data in block_data['data']]

            # 4. --- Si es seguro, crear el objeto ---
            restored_block: Block = Block(
                index = block_data['index'],
                timestamp = block_data['timestamp'],
                previous_hash = block_data['previous_hash'],
                difficulty = block_data['difficulty'],
                merkle_root = block_data['merkle_root'],
                data = data_objects,      
                nonce = block_data['nonce'],
                hash = calculated_hash,   # Usar el hash verificado/recalculado
            )

            return restored_block # Retorna el objeto Block inmutable creado.

        except KeyError as e:
            raise ValueError(f'Dato corrupto en JSON (falta clave: {e})')
        except TypeError as e:
            raise ValueError(f'Datos de transacción malformados: {e}')

    @staticmethod
    def blockchain_to_dict_list(blockchain: Blockchain) -> List[Dict[str, Any]]:
        '''
        Convierte un objeto Blockchain a una lista de diccionarios.
        '''
        # 1. Obtiene la lista de objetos Block
        blocks: List[Block] = blockchain.chain
        
        # 2. Convierte la lista de objetos Block a una lista de diccionarios
        chain_data: List[Dict[str, Any]] = [BlockSerializer.to_dict(block) for block in blocks] 
        
        # 3. Retorna la lista de diccionarios
        return chain_data

    @staticmethod
    def blockchain_from_dict_list(chain_data: List[Dict[str, Any]]) -> Blockchain:
        '''
        Convierte una lista de diccionarios (de un JSON) a un objeto Blockchain.
        '''
        blockchain: Blockchain = Blockchain()
        for block_data in chain_data:
            try:
                block: Block = BlockSerializer.from_dict(block_data)
                blockchain.add_block_forced(block)
            except ValueError as e:
                raise ValueError(f"No se pudo cargar la cadena: {e}")
        return blockchain