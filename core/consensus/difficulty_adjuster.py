# network_of_interactive_nodes/core/consensus/difficulty_adjuster.py
'''
class DifficultyAdjuster:
    Contiene la lógica pura (estática) para calcular cuándo y cómo ajustar la dificultad de la red (los 'bits').
    
    Constants:
        ADJUSTMENT_INTERVAL_BLOCKS:     (int)   Cada cuántos bloques se re-calcula la dificultad.
        EXPECTED_BLOCK_TIME_SEC:        (int)   Tiempo esperado (en segundos) que debería tomar un bloque.
        EXPECTED_TIMESPAN_SEC:          (int)   Tiempo total esperado (en segundos) para el intervalo.
        CLAMP_FACTOR:                   (int)   Tiempo real se limitará a 1/4x o 4x del esperado.

    Methods:
        should_adjust(block_index: int) -> bool: Verifica si el bloque actual es el que dispara un re-ajuste.
        
        calculate_new_bits(previous_adjustment_block: Block, current_block: Block) -> str: Calcula los 'bits' de dificultad que el bloque actual DEBERÍA tener.
            1. Calcular el tiempo real que tomó minar el intervalo
            2. Amortiguar (Clamp) el resultado para evitar cambios extremos
            3. Calcular el nuevo target (la matemática)
            4. Asegurarse de no exceder el Target Máximo (Dificultad Mínima)
            5. Convertir de vuelta a 'bits'
'''

import logging

# --- Importaciones de la Arquitectura (Herramientas) ---
from core.utils.difficulty_utils import DifficultyUtils
from core.models.block import Block

class DifficultyAdjuster:
    
    ADJUSTMENT_INTERVAL_BLOCKS: int = 100 
    EXPECTED_BLOCK_TIME_SEC: int = 60 # 1 minuto
    EXPECTED_TIMESPAN_SEC: int = ADJUSTMENT_INTERVAL_BLOCKS * EXPECTED_BLOCK_TIME_SEC # 6000 seg
    CLAMP_FACTOR: int = 4

    @staticmethod
    def should_adjust(block_index: int) -> bool:
        return (block_index > 0) and (block_index % DifficultyAdjuster.ADJUSTMENT_INTERVAL_BLOCKS == 0)

    @staticmethod
    def calculate_new_bits(previous_adjustment_block: Block, current_block: Block) -> str:
        
        actual_timespan = current_block.timestamp - previous_adjustment_block.timestamp
        expected_timespan = DifficultyAdjuster.EXPECTED_TIMESPAN_SEC
        min_timespan = expected_timespan // DifficultyAdjuster.CLAMP_FACTOR
        max_timespan = expected_timespan * DifficultyAdjuster.CLAMP_FACTOR

        if actual_timespan < min_timespan:
            actual_timespan = min_timespan
            logging.debug('Ajuste de Dificultad: Tiempo real más rápido que el límite (clamp).')
            
        if actual_timespan > max_timespan:
            actual_timespan = max_timespan
            logging.debug('Ajuste de Dificultad: Tiempo real más lento que el límite (clamp).')

        try:
            old_bits = previous_adjustment_block.bits
            old_target = DifficultyUtils.bits_to_target(old_bits)
        except (ValueError, TypeError):
             # Si los bits antiguos están corruptos, no podemos ajustar.
             logging.error("Ajuste de Dificultad: 'bits' corruptos en bloque anterior.")
             return previous_adjustment_block.bits # Retorna los bits antiguos

        # Fórmula: new_target = old_target * (actual_time / expected_time)
        new_target = (old_target * actual_timespan) // expected_timespan

        if new_target > DifficultyUtils.MAX_TARGET:
            new_target = DifficultyUtils.MAX_TARGET

        new_bits: str = DifficultyUtils.target_to_bits(new_target)
        
        logging.info(f'Ajuste Dificultad [Bloque {current_block.index}]: '
                     f'Tiempo Esperado={expected_timespan}s, '
                     f'Tiempo Real={actual_timespan}s. '
                     f'Bits: {old_bits} -> {new_bits}')

        return new_bits