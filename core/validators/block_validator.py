# network_of_interactive_nodes/core/validators/block_validator.py
'''
class BlockValidator:
    Verifica la integridad y el PoW de un Bloque ya existente.

    Methods:
        verify(block: Block) -> bool:
            1. Verificar Timestamp.
            2. Ensamblar DTO de Hashing (BlockHashingData) con datos del bloque.
            3. Recalcular el hash.
            4. Verificar integridad.
            5. Calcular Target de dificultad.
            6. Verificar PoW (hash_int <= target).
            7. Validar la integridad de TODAS las transacciones.
            8. Retornar True si todo es válido.
'''

import time

# Importaciones de la Arquitectura
from core.models.block import Block
from core.hashing.block_hasher import BlockHasher
from core.dto.block_hashing_data import BlockHashingData
from core.validators.transaction_validator import TransactionValidator
from core.utils.difficulty_utils import DifficultyUtils

class BlockValidator:

    @staticmethod
    def verify(block: Block) -> bool: 
        max_allowed_timestamp = time.time() + 7200 # 2 horas
        if block.timestamp > max_allowed_timestamp:
            return False
            
        hashing_dto: BlockHashingData = BlockHashingData(
            index = block.index,
            timestamp = block.timestamp,
            previous_hash = block.previous_hash,
            bits = block.bits, 
            merkle_root = block.merkle_root,
            nonce = block.nonce
        )
        
        recalculated_hash: str = BlockHasher.calculate(hashing_dto)
        
        if recalculated_hash != block.hash:
            return False

        target: int = DifficultyUtils.bits_to_target(block.bits)
        
        if int(recalculated_hash, 16) > target:
            return False

        if not all(TransactionValidator.verify(tx) for tx in block.data):
            return False

        return True