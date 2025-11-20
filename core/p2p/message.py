# network_of_interactive_nodes/core/p2p/message.py
'''
class Message:
    Es el "Sobre" que contiene el comando y el 'payload' (el contenido).
    
    Attributes:
        command (str):   El comando (ej. 'version', 'inv', 'block'). (12 bytes)
        payload (bytes): El contenido (el DTO del payload serializado).
'''

from dataclasses import dataclass

@dataclass(frozen = True, slots = True)
class Message:
    command: str
    payload: bytes