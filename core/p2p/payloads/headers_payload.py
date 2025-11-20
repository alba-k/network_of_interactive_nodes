# network_of_interactive_nodes/core/p2p/payloads/headers_payload.py
'''
class HeadersPayload:
    Envía una lista de 'headers' en respuesta a un 'getheaders'.

    Attributes:
        headers (List[Dict[str, Any]]): 
            Una lista de 'headers' (serializados como diccionarios).
'''

from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass(frozen = True, slots = True)
class HeadersPayload:
    headers: List[Dict[str, Any]]