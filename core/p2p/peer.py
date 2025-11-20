# network_of_interactive_nodes/core/p2p/peer.py
'''
class Peer:
    Almacena el estado y los objetos de conexión (reader/writer) para un amigo.

    Attributes:
        host (str): La dirección IP del par.
        port (int): El puerto del par.
        reader (asyncio.StreamReader): El stream para LEER datos del par.
        writer (asyncio.StreamWriter): El stream para ESCRIBIR datos al par.
'''

import asyncio
from dataclasses import dataclass

@dataclass(frozen = True, slots = True)
class Peer:
    host: str
    port: int
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter