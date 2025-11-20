# network_of_interactive_nodes/core/hashing/transaction_hasher.py
'''
class TransactionHasher:
    Contiene la lógica pura para hashear una Transaction.

    Methods:
        calculate(dto: TransactionHashingData) -> str: Calcula un hash SHA-256 determinista.
            1. Extraer la lista de hashes (data_hash) de cada DataEntry en el DTO.
            2. Crear un diccionario con la lista de hashes y el timestamp.
            3. Serializar el diccionario a un string JSON (con sort_keys=True).
            4. Codificar el string JSON a bytes (utf-8).
            5. Crear un objeto hash SHA-256 pasándole los bytes del JSON.
            6. Obtener el hash final (hexdigest) y retornarlo.
'''

import json
from hashlib import sha256
from typing import Any

# Importaciones de la arquitectura
from core.dto.transaction_hashing_data import TransactionHashingData

class TransactionHasher:

    @staticmethod
    def calculate( dto: TransactionHashingData) -> str:

        entries_hashes: list[str] = [entry.data_hash for entry in dto.entries]

        tx_dict: dict[str, Any] = {
            'entries_hashes': entries_hashes,
            'timestamp': dto.timestamp
        }

        tx_json_str: str = json.dumps(tx_dict, sort_keys=True)
        tx_json_bytes: bytes = tx_json_str.encode('utf-8')
        hash_object = sha256(tx_json_bytes)
        hex_digest: str = hash_object.hexdigest()
        return hex_digest