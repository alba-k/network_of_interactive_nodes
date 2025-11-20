# network_of_interactive_nodes/core/hashing/data_entry_hasher.py
'''
class DataEntryHasher:
    Contiene la lógica pura para hashear un DataEntry.

    Methods:
        calculate(dto: DataEntryHashingData) -> str: Calcula un hash SHA-256 determinista.
            1. Crear un diccionario con los datos del DTO.
            2. Serializar el diccionario a un string JSON (con sort_keys=True).
            3. Codificar el string JSON a bytes (utf-8).
            4. Crear un objeto hash SHA-256 pasándole los bytes del JSON.
            5. Obtener el hash final (hexdigest).
            6. Retornar el hash.
        
'''

import json
from hashlib import sha256
from typing import Any 

# Importaciones de la arquitectura
from core.dto.data_entry_hashing_data import DataEntryHashingData

class DataEntryHasher:

    @staticmethod
    def calculate( dto: DataEntryHashingData) -> str:

        entry_dict: dict[str, Any] = {
            'source_id': dto.source_id,
            'data_type': dto.data_type,
            'value': dto.value_bytes.hex(),
            'timestamp': dto.timestamp,
            'nonce': dto.nonce,
            'previous_hash': dto.previous_hash_hex,
            'metadata': dto.metadata
        }

        entry_json_str: str = json.dumps(entry_dict, sort_keys = True)
        entry_json_bytes: bytes = entry_json_str.encode('utf-8')
        hash_object = sha256(entry_json_bytes)
        hex_digest: str = hash_object.hexdigest()
        return hex_digest