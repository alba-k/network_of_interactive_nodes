# network_of_interactive_nodes/core/p2p/payloads/get_data_payload.py
'''
class GetDataPayload:
    Solicita los datos listados en el inventario.

    Attributes:
        inventory (List[InvVector]): Una lista de los hashes que pedimos.
'''

from dataclasses import dataclass
from typing import List

# Reutiliza el DTO ayudante
from core.p2p.payloads.inv_vector import InvVector 

@dataclass(frozen = True, slots = True)
class GetDataPayload:    
    inventory: List[InvVector]