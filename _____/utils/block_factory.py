# block_factory.py
'''
class BlockFactory:
    Especialista en construir bloques
    Responsable de ensamblar nuevos objetos Block.

    Attributes:

    Methods:
        create_genesis_block()-> Block:    Construye y retorna el bloque génesis.
        create_next_block(...)-> Block:    Construye un bloque candidato (sin minar).
'''

import time # Para obtener timestamps (marcas de tiempo)
import config # Importa el archivo de configuración (dificultad inicial, etc.)
from core.models.block import Block # Importa la clase de estado 'Block'
from core.models.transaction import Transaction # Importa la clase 'Transaction' (para la lista 'data')
from core.utils.crypto_utils import CryptoUtils # Importa la 'calculadora' de hashes
from typing import List, Optional # Para type hints (Listas y valores opcionales)

class BlockFactory:
    
    @staticmethod
    def create_genesis_block() -> Block:
        '''
        Construye y retorna el bloque génesis.
        '''
        index: int = 0
        timestamp: float = 1678886400.0 # Timestamp fijo
        previous_hash: Optional[str] = None # Tipo correcto para Génesis
        difficulty: int = config.INITIAL_DIFFICULTY
        nonce: int = 0
        
        # --- Crea una Transacción Génesis REAL ---
        genesis_tx: Transaction = Transaction(
            sender = 'SYSTEM',
            recipient = 'GENESIS',
            amount = 0.0,
            timestamp = timestamp,
            signature = '0' # La firma del génesis no se valida
        )
        data: List[Transaction] = [genesis_tx]
        
        
        merkle_root: str = CryptoUtils.calculate_merkle_root(data)
        
        hash_str: str = CryptoUtils.calculate_hash(
            index = index,
            timestamp = timestamp,
            previous_hash = previous_hash,
            merkle_root = merkle_root,
            difficulty = difficulty,
            nonce = nonce
        )
        
        genesis_block: Block = Block(
            index = index, 
            timestamp = timestamp, 
            previous_hash = previous_hash,
            difficulty = difficulty, 
            merkle_root = merkle_root, 
            data = data,
            nonce = nonce, 
            hash = hash_str
        )
        return genesis_block

    @staticmethod
    def create_next_block(previous_block: Block, 
                          data: List[Transaction], 
                          difficulty: int) -> Block:
        '''
        Construye un bloque candidato (sin minar)
        '''
        index: int = previous_block.index + 1
        timestamp: float = time.time()
        previous_hash: str = previous_block.hash
        nonce: int = 0
        
        merkle_root: str = CryptoUtils.calculate_merkle_root(data)
        
        hash_str = CryptoUtils.calculate_hash(
            index = index,
            timestamp = timestamp,
            previous_hash = previous_hash,
            merkle_root = merkle_root,
            difficulty = difficulty,
            nonce = nonce
        )
        
        next_block: Block = Block(
            index = index, 
            timestamp = timestamp, 
            previous_hash = previous_hash,
            difficulty = difficulty, 
            merkle_root = merkle_root, 
            data = data,
            nonce = nonce, 
            hash = hash_str
        )

        return next_block