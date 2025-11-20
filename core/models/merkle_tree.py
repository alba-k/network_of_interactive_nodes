# network_of_interactive_nodes/core/models/merkle_tree.py
'''
class MerkleTree:
    Define el objeto de modelo de datos PURO e INMUTABLE para un Árbol de Merkle.

    Attributes:
        leaves  (List[str]): Lista de hashes (hex) de las transacciones (hojas).
        root    (str):       El Merkle Root (hex) calculado.
'''

from dataclasses import dataclass
from typing import List

@dataclass(frozen=True, slots=True)
class MerkleTree:
    leaves: List[str]
    root: str