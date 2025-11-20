# network_of_interactive_nodes/core/p2p/payloads/block_payload.py
'''
class BlockPayload:
    Transporta un bloque completo (serializado).
    
    Attributes:
        block_data (Dict[str, Any]): El objeto Block (serializado a dict/JSON).
'''

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen = True, slots = True)
class BlockPayload:
    block_data: Dict[str, Any]