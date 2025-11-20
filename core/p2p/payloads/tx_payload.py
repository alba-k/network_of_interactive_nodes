# network_of_interactive_nodes/core/p2p/payloads/tx_payload.py
'''
class TxPayload:
    Transporta una transacción completa (serializada).
    
    Attributes:
        tx_data (Dict[str, Any]): El objeto Transaction (serializado a dict/JSON).
'''

from dataclasses import dataclass
from typing import Dict, Any

@dataclass(frozen = True, slots = True)
class TxPayload:
    tx_data: Dict[str, Any]