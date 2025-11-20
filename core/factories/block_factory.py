# network_of_interactive_nodes/core/factories/block_factory.py
'''
class BlockFactory:
    Ensambla y crea el objeto Block final.
    
    Methods:
        create(params: BlockCreationParams) -> Block: Crea el objeto Block final.
            1. Determinar el timestamp.
            2. Extraer la lista de hashes (tx_hash) de las transacciones.
            3. Calcular el Merkle Root.
            4. Ensamblar el DTO de hashing.
            5. Calcular el hash del bloque.
            6. Instanciar el modelo Block final con todos los datos.
            7. Retornar la instancia del bloque.
'''

from typing import List
from time import time

# Importaciones de la arquitectura
from core.models.block import Block
from core.services.merkle_root_calculator import MerkleRootCalculator
from core.hashing.block_hasher import BlockHasher
from core.dto.block_creation_params import BlockCreationParams
from core.dto.block_hashing_data import BlockHashingData

class BlockFactory:

    @staticmethod
    def create(params: BlockCreationParams) -> Block:

        final_timestamp: int = params.timestamp if params.timestamp is not None else int(time())

        tx_hashes: List[str] = [tx.tx_hash for tx in params.transactions]

        merkle_root: str = MerkleRootCalculator.calculate(
            tx_hashes = tx_hashes, 
            log_layers = params.log_merkle_layers
        )

        hashing_dto: BlockHashingData = BlockHashingData(
            index = params.index,
            timestamp = final_timestamp,
            previous_hash = params.previous_hash,
            bits = params.bits,
            merkle_root = merkle_root,
            nonce = params.nonce
        )

        block_hash: str = BlockHasher.calculate(hashing_dto)

        new_block: Block = Block(
            index = params.index,
            timestamp = final_timestamp,
            previous_hash = params.previous_hash,
            bits = params.bits,
            merkle_root = merkle_root,
            data = params.transactions,
            nonce = params.nonce,
            hash = block_hash
        )
        
        return new_block