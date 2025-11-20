# network_of_interactive_nodes/core/p2p/payloads/inv_payload.py
'''
class InvPayload:
    Anuncia (chisme) que este nodo TIENE datos.

    Attributes:
        inventory (List[InvVector]): Una lista de los hashes que anunciamos.
'''

from dataclasses import dataclass
from typing import List

# El DTO ayudante
from core.p2p.payloads.inv_vector import InvVector 

@dataclass(frozen = True, slots = True)
class InvPayload:
    inventory: List[InvVector]