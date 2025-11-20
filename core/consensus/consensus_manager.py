# network_of_interactive_nodes/core/consensus/consensus_manager.py
'''
class ConsensusManager:
    Servicio que aplica las reglas de consenso y gestiona la Blockchain.
    Implementa el método de "Validar" ANTES de añadir un bloque.

    Attributes:
        _blockchain (Blockchain): La instancia del contenedor puro de la cadena.
        
    Methods:
        __init__(blockchain): Guardar la instancia de la blockchain.

        add_block(block, public_key_map) -> bool:
            1. Validación de Conexión (Falla Rápido)
            2. Logica de ajuste de dificultad.
            3. Validación de PoW e Integridad (Delegar a "Herramienta")
            4. Validación de Firmas (Delegar a "Herramienta")
            5. Éxito
'''

import logging
from typing import Dict, Any, TYPE_CHECKING
from Crypto.PublicKey.ECC import EccKey

# Importaciones de la arquitectura
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.validators.block_validator import BlockValidator
from core.validators.transaction_verifier import TransactionVerifier
from core.consensus.difficulty_adjuster import DifficultyAdjuster

if TYPE_CHECKING:
    EccKeyType = Any
else:
    EccKeyType = EccKey

class ConsensusManager:

    def __init__(self, blockchain: Blockchain):
        self._blockchain: Blockchain = blockchain

    def add_block(self, new_block: Block, public_key_map: Dict[str, EccKeyType]) -> bool:
        
        last_block: Block | None = self._blockchain.last_block
        
        if last_block:
            if new_block.previous_hash != last_block.hash:
                logging.warning('Error Consenso: Hash previo no coincide.')
                return False
            if new_block.index != (last_block.index + 1):
                logging.warning('Error Consenso: Índice de bloque inválido.')
                return False
        
        if DifficultyAdjuster.should_adjust(new_block.index):
            
            prev_adj_block_index = new_block.index - DifficultyAdjuster.ADJUSTMENT_INTERVAL_BLOCKS
            
            if prev_adj_block_index < 0:
                logging.error(f'Error Consenso: Índice de ajuste inválido {prev_adj_block_index}.')
                return False 

            try:
                prev_adj_block = self._blockchain.chain[prev_adj_block_index]
            except IndexError:

                logging.error(f'Error Consenso: No se pudo encontrar el bloque de anclaje {prev_adj_block_index} (IndexError).')
                return False
            
            expected_bits = DifficultyAdjuster.calculate_new_bits(prev_adj_block, new_block)
            
            if new_block.bits != expected_bits:
                
                logging.warning(f'Error Consenso: Bloque {new_block.index} rechazado. '
                                f'Dificultad incorrecta. Esperada: {expected_bits}, Recibida: {new_block.bits}')
                return False
        
        if not BlockValidator.verify(new_block):
            logging.warning(f'Error Consenso: Falla de PoW o integridad del bloque {new_block.index}.')
            return False

        for tx in new_block.data:
                        
            if tx.signature is None: continue 
            if not tx.entries: continue
            
            data_owner_id: str = tx.entries[0].source_id
            public_key = public_key_map.get(data_owner_id)
            
            if not public_key:
                logging.warning(f'Error Consenso: Clave pública no encontrada para {data_owner_id}')
                return False

            if not TransactionVerifier.verify(public_key, tx.tx_hash, tx.signature):
                logging.warning(f'Error Consenso: Firma inválida para TX {tx.tx_hash}')
                return False

        self._blockchain.add_block_forced(new_block)
        return True