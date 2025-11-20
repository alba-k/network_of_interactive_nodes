# crypto_utils.py 
'''
class CrytoUtils:
    Especialista en cálculos criptográficos (Hashing y Firmas).
    
    Attributes:
    
    Methods:
        calculate_merkle_root(data)->  str:         Calcula el Merkle Root.
        calculate_hash(...):->         str:         Calcula el hash del bloque.
        verify_signature(...):->       bool:        Verifica una firma digital ECDSA.
'''

import json # Para serializar (convertir) objetos Python a strings JSON
import binascii # Para convertir entre formato hexadecimal (hex) y bytes
from typing import List, Dict, Any, Optional # Para type hints (Listas, Diccionarios, etc.)
from hashlib import sha256 # Importa la función de hash SHA-256
from dataclasses import asdict # Herramienta para convertir un dataclass a un diccionario
from core.models.transaction import Transaction # Importa la clase de estado 'Transaction'
import ecdsa  # type: ignore 
from ecdsa.curves import SECP256k1 # type: ignore # La misma curva que usa Bitcoin

class CryptoUtils:

    @staticmethod
    def calculate_merkle_root(data: List[Transaction]) -> str:
        '''
        Calcula el Merkle Root (hash de los datos/transacciones).
        '''

        # 1. CONVERTIR LOS OBJETOS 'TRANSACTION' EN DICCIONARIOS
        data_as_dicts: List[Dict[str, Any]] = [asdict(tx) for tx in data]
        
        # 2. CONVERTIR LA LISTA DE DICCIONARIOS A UN STRING JSON
        data_string: str = json.dumps(data_as_dicts, sort_keys=True)
        
        # 3. CODIFICAR, HASHEAR Y DEVOLVER EL HASH COMO TEXTO (HEXADECIMAL)
        hash_object = sha256(data_string.encode('utf-8'))
        return hash_object.hexdigest()

    @staticmethod
    def calculate_hash(index: int, 
                       timestamp: float, 
                       previous_hash: Optional[str],
                       merkle_root: str, # <--- ¡IMPORTANTE! Se usa en el cálculo
                       difficulty: int,
                       nonce: int) -> str:
        '''
        Calcula el hash SHA-256 de la cabecera del bloque.
        '''
        
        # 1. AGRUPAR TODOS LOS DATOS DE LA CABECERA EN UN DICCIONARIO
        header_content: Dict[str, Any] = {
            'index': index,
            'timestamp': timestamp,
            'previous_hash': previous_hash,
            'merkle_root': merkle_root, 
            'difficulty': difficulty,
            'nonce': nonce 
        }
        
        # 2. CONVERTIR EL DICCIONARIO DE LA CABECERA A UN STRING JSON
        header_string: str = json.dumps(header_content, sort_keys=True)
        
        # 3. CODIFICAR, HASHEAR Y DEVOLVER EL HASH COMO TEXTO (HEXADECIMAL)
        hash_object = sha256(header_string.encode('utf-8'))
        return hash_object.hexdigest()
    
    @staticmethod
    def sha256(data: bytes) -> bytes:
        """Calcula el hash SHA-256 de los datos."""
        return sha256(data).digest() 

    @staticmethod
    def verify_signature(public_key_hex: str, 
                         signature_hex: str, 
                         data_hash: str) -> bool:
        '''
        Verifica una firma digital ECDSA (curva SECP256k1).
        '''
        try:
            # 1. DECODIFICAR LA CLAVE PÚBLICA (bytes)
            public_key_bytes: bytes = bytes.fromhex(public_key_hex)
            
            # Quita el prefijo 0x04 si está presente (es un estándar de claves no comprimidas)
            if public_key_bytes.startswith(b'\x04'):
                 public_key_bytes = public_key_bytes[1:]
            
            # CORRECCIÓN: Silenciamos el aviso de 'from_string is partially unknown' (image_493204.png)
            vk = ecdsa.VerifyingKey.from_string(public_key_bytes, curve = SECP256k1) # type: ignore
            
            # 2. DECODIFICAR LA FIRMA y HASH
            signature_bytes: bytes = bytes.fromhex(signature_hex)
            data_hash_bytes: bytes = bytes.fromhex(data_hash) # El mensaje original

            # 3. LA VERIFICACIÓN (hashfunc=sha256 es crucial)
            return vk.verify(signature_bytes, data_hash_bytes, hashfunc=sha256) # type: ignore

        except (ecdsa.BadSignatureError, ValueError, binascii.Error, IndexError):
            # Captura errores comunes de formato o firmas inválidas.
            return False
        except Exception:
            # CAPTURA CUALQUIER OTRO ERROR INESPERADO
            return False