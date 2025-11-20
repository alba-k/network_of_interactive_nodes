# network_of_interactive_nodes/core/p2p/payloads/version_payload.py
'''
class VersionPayload:
    Usado para el "apretón de manos" P2P.

    Attributes:
        protocol_version    (int):  La versión del protocolo P2P que hablamos.
        services            (int):  Banderas (flags) que indican los roles (Punto 6).
        timestamp           (int):  Marca de tiempo UNIX de este nodo.
        best_height         (int):  El índice (altura) del último bloque que tiene este nodo.
'''

from dataclasses import dataclass

@dataclass(frozen = True, slots = True)
class VersionPayload:
    protocol_version: int
    services: int
    timestamp: int
    best_height: int