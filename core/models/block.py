# network_of_interactive_nodes/core/models/block.py
'''
class Block:
    Representa un bloque inmutable en la cadena.

    Attributes:
        index           (int):                    Indice del bloque (altura).
        timestamp       (int):                    Timestamp de creación (UNIX).
        previous_hash   (Optional[str]):          Hash del bloque anterior.
        bits            (str):                    Dificultad en formato compacto 'bits'.
        merkle_root     (str):                    Merkle Root de las transacciones.
        data            (List[Transaction]):      Lista de transacciones incluidas.
        nonce           (int):                    Nonce (prueba de trabajo).
        hash            (str):                    Hash (Doble SHA-256) de la cabecera.
        mining_time     (Optional[float]):        Tiempo que tomó minar (opcional).
'''

from dataclasses import dataclass, field
from typing import List, Optional

# Importaciones de la arquitectura
from core.models.transaction import Transaction

@dataclass(frozen=True, slots=True)
class Block:
    index: int
    timestamp: int
    previous_hash: Optional[str]
    bits: str 
    merkle_root: str
    data: List[Transaction]
    nonce: int
    hash: str
    mining_time: Optional[float] = field(default = None, compare = False)