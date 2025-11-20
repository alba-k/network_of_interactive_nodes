# network_of_interactive_nodes/core/p2p/p2p_message_serializer.py
'''
class P2PMessageSerializer:
    Contiene la lógica pura para serializar un 'command' (str) y un 'payload' (DTO) en un paquete de 'bytes' crudos listos para enviar por la red.

    Attributes (Constants):
        COMMAND_LENGTH  (int): Tamaño fijo en bytes para el 'command' (12).
        HEADER_FORMAT   (str): La plantilla 'struct' para el header binario.
        HEADER_SIZE     (int): El tamaño total en bytes del header.

    Methods:
        serialize(command: str, payload_dto: Any) -> bytes: Toma un 'command' y un DTO, y realiza todos los pasos de serialización (DTO->JSON->bytes, checksum, header).
            1. Validar el Payload
            2. Serializar Payload (DTO -> JSON -> bytes)
            3. Calcular Checksum y Tamaño
            4. Codificar Comando (con padding)
            5. Empaquetar el Header
            6. Combinar y Retornar

        _calculate_checksum(payload: bytes) -> bytes: Método helper privado para calcular el checksum (doble SHA-256).
'''

import json
import struct 
import hashlib
from dataclasses import asdict, is_dataclass
from typing import Any

class P2PMessageSerializer:

    COMMAND_LENGTH = 12 
    HEADER_FORMAT = f'<{COMMAND_LENGTH}sL4s'
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

    @staticmethod
    def _calculate_checksum(payload: bytes) -> bytes:
        return hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]

    @staticmethod
    def serialize(command: str, payload_dto: Any) -> bytes:
        if not is_dataclass(payload_dto) or isinstance(payload_dto, type):
            raise ValueError('El payload debe ser un OBJETO (instancia) dataclass (DTO P2P)')
            
        payload_dict = asdict(payload_dto)
        payload_json = json.dumps(payload_dict, sort_keys=True)
        payload_bytes = payload_json.encode('utf-8')
        
        checksum_bytes = P2PMessageSerializer._calculate_checksum(payload_bytes)
        payload_size = len(payload_bytes)
        
        command_bytes = command.encode('utf-8').ljust(P2PMessageSerializer.COMMAND_LENGTH, b'\x00')
        
        header = struct.pack(P2PMessageSerializer.HEADER_FORMAT, command_bytes, payload_size, checksum_bytes)
        return header + payload_bytes