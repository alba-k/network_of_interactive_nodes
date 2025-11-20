# network_of_interactive_nodes/core/dto/block_hashing_data.py
'''
class BlockHashingData:
    Agrupa los datos que el BlockHasher necesita para su cálculo.

    Attributes:
        index           (int):              Indice del bloque (altura).
        timestamp       (int):              Timestamp de creación (segundos UNIX).
        previous_hash   (Optional[str]):    Hash del bloque anterior.
        bits            (str):              Dificultad en formato compacto 'bits'.
        merkle_root     (str):              Merkle Root de las transacciones.
        nonce           (int):              Nonce encontrado.
'''

from dataclasses import dataclass
from typing import Optional

@dataclass(frozen = True, slots = True)
class BlockHashingData:
    index: int
    timestamp: int
    previous_hash: Optional[str]
    bits: str
    merkle_root: str
    nonce: int