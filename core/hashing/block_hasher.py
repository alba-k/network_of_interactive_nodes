# network_of_interactive_nodes/core/hashing/block_hasher.py
'''
class BlockHasher:
    Contiene la lógica pura para hashear la cabecera de un Bloque (Doble SHA-256).

    Methods:
        calculate(dto: BlockHashingData) -> str: Calcula un hash SHA-256 doble (estilo Bitcoin) determinista.
            1. Crear un diccionario (dict) con los datos del DTO.
            2. Manejar el 'previous_hash' (si es None, usar string vacío).
            3. Serializar el diccionario a un string JSON (con sort_keys=True).
            4. Codificar el string JSON a bytes (utf-8).
            5. Calcular el primer hash SHA-256 (obteniendo bytes/digest).
            6. Calcular el segundo hash SHA-256 sobre el primer hash (obteniendo hex/hexdigest).
            7. Retornar el hash final hexadecimal.
'''

import hashlib
import json
from typing import Any, Dict

# Importaciones de la arquitectura
from core.dto.block_hashing_data import BlockHashingData

class BlockHasher:

    @staticmethod
    def calculate(dto: BlockHashingData) -> str:
        
        header_dict: Dict[str, Any] = {
            'index': dto.index,
            'timestamp': dto.timestamp,
            'previous_hash': (dto.previous_hash or ''),
            'bits': dto.bits,
            'merkle_root': dto.merkle_root,
            'nonce': dto.nonce
        }
        
        header_json_str: str = json.dumps(header_dict, sort_keys = True)
        header_bytes: bytes = header_json_str.encode('utf-8')
        first_hash_bytes: bytes = hashlib.sha256(header_bytes).digest()
        second_hash_hex: str = hashlib.sha256(first_hash_bytes).hexdigest()
        return second_hash_hex