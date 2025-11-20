# core/dto/proof_of_work_params.py
'''
class ProofOfWorkParams:
    DTO (Data Transfer Object) para los parámetros de ejecución 
    de la Prueba de Trabajo (PoW).

Attributes:
    candidate_block (Block): El bloque candidato (inmutable) 
                             que se usará como base para el minado.
    difficulty (int): Dificultad actual (número de ceros requeridos).
'''

from dataclasses import dataclass

# Importaciones de la arquitectura
from core.models.block import Block

@dataclass(frozen=True)
class ProofOfWorkParams:
    
    candidate_block: Block
    difficulty: int