# network_of_interactive_nodes/core/dto/block_creation_params.py
'''
class BlockCreationParams:
    Agrupa todos los datos *crudos* necesarios por la BlockFactory.

    Attributes:
        index               (int):                    Indice del bloque (altura).
        transactions        (List[Transaction]):      Lista de transacciones a incluir.
        previous_hash       (Optional[str]):          Hash del bloque anterior.
        bits                (str):                    Dificultad en formato compacto 'bits' (ej: "1d00ffff").
        nonce               (int):                    Nonce (debe ser provisto si no se mina).
        timestamp           (Optional[int]):          Timestamp (si se provee externamente).
        log_merkle_layers   (bool):                   Flag para el logging del Merkle Calculator.
'''

from dataclasses import dataclass
from typing import List, Optional

# Importaciones de la arquitectura
from core.models.transaction import Transaction

@dataclass(frozen = True, slots = True)
class BlockCreationParams:
    index: int
    transactions: List[Transaction]
    previous_hash: Optional[str]
    bits: str
    nonce: int
    timestamp: Optional[int] = None
    log_merkle_layers: bool = False