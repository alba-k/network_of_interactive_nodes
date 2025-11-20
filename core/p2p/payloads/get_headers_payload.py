# network_of_interactive_nodes/core/p2p/payloads/get_headers_payload.py
'''
class GetHeadersPayload:
    Solicita una lista de 'headers' a un par, comenzando desde un 'hash'.

    Attributes:
        protocol_version (int):       Versión del protocolo P2P.
        locator_hashes   (List[str]): Lista de 'hashes' que tenemos (para que el otro nodo sepa desde dónde empezar).
        hash_stop        (str):       'hash' del último 'header' que queremos (o 0).
'''

from dataclasses import dataclass
from typing import List

@dataclass(frozen = True, slots = True)
class GetHeadersPayload:
    protocol_version: int
    locator_hashes: List[str]
    hash_stop: str