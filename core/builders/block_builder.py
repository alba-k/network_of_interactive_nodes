# network_of_interactive_nodes/core/builders/block_builder.py
'''
class BlockBuilder:
    Orquesta el ciclo de vida completo de la creación y minado de un Bloque (Proof-of-Work).
    Implementa el proceso de minería optimizado.

    *** CORRECCIÓN: Usa object.__setattr__ para mutar DTOs congelados (frozen). ***

    Methods:
        build(index, transactions, previous_hash, bits) -> Block:
            1. Preparar datos estáticos (Merkle, Target).
            2. Preparar DTO reutilizable.
            3. Bucle de minería de alta velocidad (Update -> Hash -> Check).
            4. Retornar bloque minado.
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

    # Límite estándar de 4 bytes para el nonce (2^32 - 1)
    MAX_NONCE: int = 4294967295 

    @staticmethod
    def build(
        index: int, 
        transactions: List[Transaction], 
        previous_hash: Optional[str],
        bits: str
    ) -> Block:
        
        start_time: float = time.time()
        
        # 1. Preparación de Datos Estáticos (Heavy lifting fuera del bucle)
        tx_hashes: List[str] = [tx.tx_hash for tx in transactions]
        merkle_root: str = MerkleRootCalculator.calculate(tx_hashes=tx_hashes)
        target: int = DifficultyUtils.bits_to_target(bits)
        
        nonce: int = 0
        timestamp: int = int(time.time())
        
        # 2. Instanciación Única del DTO (Optimización de Memoria)
        hashing_dto: BlockHashingData = BlockHashingData(
            index = index,
            timestamp = timestamp,
            previous_hash = previous_hash, 
            bits = bits,
            merkle_root = merkle_root, 
            nonce = nonce
        )
        
        # 3. Bucle de Minería Optimizado
        while nonce < BlockBuilder.MAX_NONCE:
        
            # -----------------------------------------------------------------
            # [FIX READ-ONLY ERROR]
            # Como BlockHashingData es 'frozen=True', no podemos hacer .nonce = ...
            # Usamos object.__setattr__ para saltarnos esa restricción SOLO AQUÍ
            # por razones de rendimiento crítico.
            # -----------------------------------------------------------------
            object.__setattr__(hashing_dto, 'nonce', nonce)
            
            # Cálculo del Hash (Usa struct binario internamente)
            block_hash: str = BlockHasher.calculate(hashing_dto)
            
            # Verificación de Dificultad
            if int(block_hash, 16) <= target:
                
                # ¡Éxito! Bloque encontrado.
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
                
                # Agregamos metadatos de rendimiento
                final_block = replace(mined_block, mining_time = round(duration, 4))
                
                return final_block
            
            # Siguiente intento
            nonce += 1
            
        raise RuntimeError(f'Fallo de minería: Nonce agotado para el bloque {index}.')