# core/dto/proof_of_work_result.py
'''
class ProofOfWorkResult:
    DTO (Data Transfer Object) para el resultado de ejecutar PoW.
    Agrupa los datos de retorno del servicio de minado.

    Attributes:
        mined_block (Block): Bloque final minado con nonce y hash válidos.
        mining_time (float): Tiempo empleado en el minado (segundos).
'''

from dataclasses import dataclass

# Importaciones de la arquitectura
from core.models.block import Block

@dataclass(frozen=True)
class ProofOfWorkResult:
    
    mined_block: Block
    mining_time: float