# network_of_interactive_nodes/core/security/transaction_signer.py
'''
Class TransactionSigner:
    Contiene la lógica pura para firmar un hash de transacción usando el esquema ECDSA (Curva NIST P-256).

    *** ACTUALIZACIÓN: Implementa Firmas Deterministas (RFC 6979) y manejo eficiente de bytes. ***

    Methods:
        sign(private_key: EccKey, tx_hash: str) -> str: Firma un hash de transacción.
            1. Convertir el hash hex a bytes crudos.
            2. Crear objeto Hash (SHA256) sobre los bytes crudos.
            3. Crear firmador Determinista (RFC 6979).
            4. Firmar.
            5. Retornar firma en hex.
'''

from Crypto.PublicKey.ECC import EccKey
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from binascii import hexlify, unhexlify
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    EccKeyType = Any
else:
    EccKeyType = EccKey


class TransactionSigner:

    @staticmethod
    def sign(private_key: EccKeyType, tx_hash: str) -> str: 
        
        # 1. Eficiencia: Convertir el Hex String (64 chars) a Bytes crudos (32 bytes)
        # Esto es más estándar que hashear la representación string utf-8.
        try:
            raw_hash_bytes = unhexlify(tx_hash)
        except Exception:
            # Fallback defensivo por si acaso llega algo que no es hex puro
            raw_hash_bytes = tx_hash.encode('utf-8')

        # 2. Preparar el objeto Hash para PyCryptodome
        # Hasheamos los datos una vez más antes de firmar (Doble Hash implícito en el flujo)
        hash_obj = SHA256.new(raw_hash_bytes)
        
        # 3. Seguridad: Usar RFC 6979 (Determinista)
        # Elimina la dependencia de un RNG (Generador de números aleatorios) fuerte.
        # Si firmas lo mismo 2 veces, obtienes la misma firma.
        signer = DSS.new(private_key, 'deterministic-rfc6979') # type: ignore
        
        signature_bytes: bytes = signer.sign(hash_obj)
        signature_hex: str = hexlify(signature_bytes).decode('utf-8')
        
        return signature_hex