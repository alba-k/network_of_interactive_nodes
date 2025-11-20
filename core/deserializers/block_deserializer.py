# network_of_interactive_nodes/core/deserializers/block_deserializer.py
'''
class BlockDeserializer:
    Lógica pura para deserializar un dict a un Block.

    Methods:
        from_dict(data: dict) -> Block: Reconstruye un Block desde un diccionario.
            1. Deserializar la lista de Transacciones.
            2. Extraer los datos raíz del bloque.
            3. Extraer los hashes de las transacciones deserializadas.
            4. Recalcular el Merkle Root.
            5. Verificar la integridad del Merkle Root.
            6. Ensamblar el DTO (BlockHashingData) para recalcular el hash del bloque.
            7. Llamar al Hasher para recalcular el hash del bloque.
            8. Verificar la integridad del Hash.
            9. Construir el objeto Block final.
            10. Retornar el objeto reconstruido.
'''

from typing import Any, List, Dict

# Importaciones de la arquitectura
from core.models.block import Block
from core.models.transaction import Transaction
from core.hashing.block_hasher import BlockHasher
from core.dto.block_hashing_data import BlockHashingData
from core.deserializers.transaction_deserializer import TransactionDeserializer
from core.services.merkle_root_calculator import MerkleRootCalculator

class BlockDeserializer:

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Block:
        
        try:
            transactions: List[Transaction] = [
                TransactionDeserializer.from_dict(tx_data)
                for tx_data in data['data']
            ]

            index: int = int(data['index'])
            timestamp: int = int(data['timestamp'])
            previous_hash: str | None = data.get('previous_hash')
            bits: str = data['bits']
            merkle_root_stored: str = data['merkle_root']
            nonce: int = int(data['nonce'])
            block_hash_stored: str = data['hash']
            mining_time: float | None = data.get('mining_time')

            tx_hashes: List[str] = [tx.tx_hash for tx in transactions]

            if not tx_hashes:
                # Un bloque (excepto quizás el Génesis si se maneja especial) debe tener txs
                raise ValueError('Corrupción de datos: Un bloque no puede tener cero transacciones.')
            
            calculated_merkle_root: str = MerkleRootCalculator.calculate(tx_hashes)

            if calculated_merkle_root != merkle_root_stored:
                raise ValueError('Corrupción de datos: El Merkle Root no coincide con las transacciones.')

            hashing_dto: BlockHashingData = BlockHashingData(
                index = index,
                timestamp = timestamp,
                previous_hash = previous_hash,
                bits = bits,
                merkle_root = merkle_root_stored, # Usamos el root ya verificado
                nonce = nonce
            )

            calculated_hash: str = BlockHasher.calculate(hashing_dto)

            if calculated_hash != block_hash_stored:
                raise ValueError('Corrupción de datos: El hash del Bloque no coincide.')

            reconstructed_block: Block = Block(
                index = index,
                timestamp = timestamp,
                previous_hash = previous_hash,
                bits = bits,
                merkle_root = merkle_root_stored,
                data = transactions,
                nonce = nonce,
                hash = block_hash_stored,
                mining_time = mining_time
            )

            return reconstructed_block

        except (KeyError, ValueError, TypeError) as e:
            # Captura errores de formato (ej. falta 'index') o fallos de verificación
            raise ValueError(f'Dato corrupto o malformado en Block JSON ({e})')