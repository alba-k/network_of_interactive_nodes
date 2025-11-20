# network_of_interactive_nodes/core/hashing/merkle_hasher.py
'''
class MerkleHasher:
    Contiene la lógica pura para hashear un par de nodos Merkle (Bitcoin-style).

    Methods:
        hash_pair(left_hex: str, right_hex: str) -> str: Combina y hashea dos strings hexadecimales.
            1. Convertir el hash 'left' (hex) a bytes.
            2. Convertir el hash 'right' (hex) a bytes.
            3. Concatenar los bytes (left + right).
            4. Calcular el hash doble (delegando a _double_sha256).
            5. Convertir el hash final (bytes) a un string hexadecimal.
            6. Retornar el string hexadecimal.
            
        _double_sha256(data: bytes) -> bytes: Helper privado que aplica doble SHA-256 (Bitcoin-style) a bytes.
            1. Calcular el primer hash SHA-256 sobre los datos de entrada.
            2. Obtener el digest (bytes) del primer hash.
            3. Calcular el segundo hash SHA-256 sobre el primer digest.
            4. Obtener el digest (bytes) final.
            5. Retornar el digest final.
'''

import hashlib
from binascii import unhexlify, hexlify

class MerkleHasher:

    @staticmethod
    def hash_pair(left_hex: str, right_hex: str) -> str:
        
        left_bytes: bytes = unhexlify(left_hex)
        right_bytes: bytes = unhexlify(right_hex)
        combined_bytes: bytes = left_bytes + right_bytes
        hash_bytes: bytes = MerkleHasher._double_sha256(combined_bytes)
        hash_hex: str = hexlify(hash_bytes).decode('utf-8')
        return hash_hex
    
    @staticmethod
    def _double_sha256(data: bytes) -> bytes:
        
        first_hash_obj = hashlib.sha256(data)
        first_hash_bytes: bytes = first_hash_obj.digest()
        second_hash_obj = hashlib.sha256(first_hash_bytes)
        final_hash_bytes: bytes = second_hash_obj.digest()
        return final_hash_bytes