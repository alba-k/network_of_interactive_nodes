# network_of_interactive_nodes/core/consensus/difficulty_adjuster.py
'''
class DifficultyAdjuster:
    Logica pura para calcular y ajustar la dificultad de la red (los 'bits').
    
    Methods:
        should_adjust(block_index: int) -> bool: Verifica si el bloque actual es el que dispara un re-ajuste.
        
        calculate_new_bits(previous_adjustment_block: Block, current_block: Block) -> str: Calcula los 'bits' de dificultad.
            1. Calcular el tiempo real que tomó minar el intervalo.
            2. Amortiguar (Clamp) el resultado usando configuración.
            3. Calcular el nuevo target (la matemática).
            4. Asegurarse de no exceder el Target Máximo.
            5. Convertir de vuelta a 'bits'.
'''

import logging

# Importación de Configuración 
from config import Config

# Importacion de arquitectura
from core.utils.difficulty_utils import DifficultyUtils
from core.models.block import Block

class DifficultyAdjuster:

    @staticmethod
    def should_adjust(block_index: int) -> bool:
        interval: int = Config.DIFFICULTY_ADJUSTMENT_INTERVAL
        return (block_index > 0) and (block_index % interval == 0)

    @staticmethod
    def calculate_new_bits(previous_adjustment_block: Block, current_block: Block) -> str:
        
        actual_timespan: int = current_block.timestamp - previous_adjustment_block.timestamp
        
        expected_timespan: int = Config.DIFFICULTY_ADJUSTMENT_INTERVAL * Config.BLOCK_TIME_TARGET_SEC
        
        clamp_factor: int = Config.DIFFICULTY_CLAMP_FACTOR
        min_timespan: int = expected_timespan // clamp_factor
        max_timespan: int = expected_timespan * clamp_factor

        if actual_timespan < min_timespan:
            actual_timespan = min_timespan
            logging.debug('Ajuste de Dificultad: Tiempo real más rápido que el límite (clamp).')
            
        if actual_timespan > max_timespan:
            actual_timespan = max_timespan
            logging.debug('Ajuste de Dificultad: Tiempo real más lento que el límite (clamp).')

        try:
            old_bits: str = previous_adjustment_block.bits
            old_target: int = DifficultyUtils.bits_to_target(old_bits)
        except (ValueError, TypeError):
            logging.error('''Ajuste de Dificultad: 'bits' corruptos en bloque anterior.''')
            return previous_adjustment_block.bits 

        new_target: int = (old_target * actual_timespan) // expected_timespan

        if new_target > DifficultyUtils.MAX_TARGET:
            new_target = DifficultyUtils.MAX_TARGET

        new_bits: str = DifficultyUtils.target_to_bits(new_target)
        
        logging.info(f'Ajuste Dificultad [Bloque {current_block.index}]: '
                     f'Tiempo Esperado={expected_timespan}s, '
                     f'Tiempo Real={actual_timespan}s. '
                     f'Bits: {old_bits} -> {new_bits}')

        return new_bits