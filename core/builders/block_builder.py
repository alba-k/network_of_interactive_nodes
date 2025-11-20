# network_of_interactive_nodes/core/builders/block_builder.py
'''
class BlockBuilder:
    Orquesta el ciclo de vida completo de la creación y minado de un Bloque (Proof-of-Work).
    Implementa el proceso de minería.

    Methods:
        build(index, transactions, previous_hash, bits) -> Block:
            1. Extraer la lista de hashes de las transacciones.
            2. Calcular el Merkle Root.
            3. Calcular el Target de dificultad.
            4. Iniciar el bucle de minería (PoW) con un timestamp.
            5. En cada iteración:
                a. Ensamblar DTO de Hashing con el nonce actual.
                b. Calcular el hash del bloque.
                c. Verificar si (hash_int <= target).
            6. Si se encuentra el hash:
                a. Ensamblar DTO de Creación.
                b. Instanciar Bloque (via Factory).
                c. Clonar el Bloque (usando 'replace') para añadir 'mining_time'.
                d. Retornar el Bloque minado final.
            7. Si se agota el nonce, lanzar una excepción.
'''

import time
from typing import List, Optional
from dataclasses import replace

# Importaciones de la Arquitectura
from core.models.block import Block
from core.models.transaction import Transaction
from core.factories.block_factory import BlockFactory
from core.hashing.block_hasher import BlockHasher
from core.services.merkle_root_calculator import MerkleRootCalculator
from core.dto.block_creation_params import BlockCreationParams
from core.dto.block_hashing_data import BlockHashingData
from core.utils.difficulty_utils import DifficultyUtils

class BlockBuilder:

    @staticmethod
    def build(
        index: int, 
        transactions: List[Transaction], 
        previous_hash: Optional[str],
        bits: str
    ) -> Block:
        
        start_time: float = time.time()
        tx_hashes: List[str] = [tx.tx_hash for tx in transactions]
        merkle_root: str = MerkleRootCalculator.calculate(tx_hashes=tx_hashes)
        target: int = DifficultyUtils.bits_to_target(bits)
        nonce: int = 0
        timestamp: int = int(time.time())
        
        while nonce < 2**32:
        
            hashing_dto: BlockHashingData = BlockHashingData(
                index = index,
                timestamp = timestamp,
                previous_hash = previous_hash, 
                bits = bits,
                merkle_root = merkle_root, 
                nonce = nonce
            )
            
            block_hash: str = BlockHasher.calculate(hashing_dto)
            
            if int(block_hash, 16) <= target:
                
                duration: float = time.time() - start_time
                creation_params: BlockCreationParams = BlockCreationParams(
                    index = index, 
                    transactions = transactions,
                    previous_hash = previous_hash, 
                    bits = bits,
                    nonce = nonce, 
                    timestamp = timestamp
                )
                
                mined_block: Block = BlockFactory.create(creation_params)
                final_block = replace(mined_block, mining_time = round(duration, 4)
                )
                return final_block
            nonce += 1
        raise RuntimeError(f'Fallo de minería: Nonce agotado para el bloque {index}.')