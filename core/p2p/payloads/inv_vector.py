# network_of_interactive_nodes/core/p2p/payloads/inv_vector.py
'''
class InvVector:
    Representa un único objeto (un hash) en el inventario.

    Attributes:
        type (int): El tipo de objeto (ej. 1 = TX, 2 = Block).
        hash (str): El hash (hex) del objeto.
'''

from dataclasses import dataclass

@dataclass(frozen = True, slots = True)
class InvVector:
    type: int
    hash: str