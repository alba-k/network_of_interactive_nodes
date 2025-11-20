# i_consensus.py 
'''
    Define la Interfaz (Contrato) para un algoritmo de Consenso.

    Attributes:

    Methods:
        execute(candidate_block)->      Block:      Ejecuta el proceso de consenso sobre un bloque candidato y retorna un bloque finalizado.
        validate(block)->               bool:       Verifica si un bloque dado cumple las reglas de consenso.
        adjust_parameters(**kwargs):    Ajusta parámetros internos (ej. dificultad, staking).
'''

from abc import ABC, abstractmethod # Importa helpers para crear Clases Abstractas (Interfaces)
from core.models.block import Block # Importa la clase de estado 'Block'
from typing import Any # Importa el type hint 'Any' (Cualquier tipo)

class IConsensus(ABC):

    @abstractmethod
    def execute(self, candidate_block_data: Block) -> Block: 
        '''
        Ejecuta el proceso de consenso (PoW, PoS, etc.) y 
        DEVUELVE un nuevo bloque finalizado e inmutable.
        '''
        pass

    @abstractmethod
    def validate(self, block: Block) -> bool:
        '''
        Verifica si un bloque cumple con las reglas de consenso.
        '''
        pass

    @abstractmethod
    def adjust_parameters(self, **kwargs: Any) -> None:
        '''
        Ajusta los parámetros del consenso (ej: dificultad, recompensas).
        '''
        pass