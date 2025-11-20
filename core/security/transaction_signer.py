# network_of_interactive_nodes/core/security/transaction_signer.py
'''
Class TransactionSigner:
    Contiene la lógica pura para firmar un hash de transacción usando el esquema ECDSA (Curva NIST P-256).

    Methods:
        sign(private_key: EccKey, tx_hash: str) -> str: Firma un hash de transacción.
            1. Hashear el hash de la transacción (tx_hash) con SHA-256.
            2. Crear un firmador ECDSA (DSS) con la clave privada.
            3. Firmar el hash SHA-256 resultante.
            4. Convertir la firma (bytes) a un string hexadecimal.
            5. Retornar el string hexadecimal.
'''

from Crypto.PublicKey.ECC import EccKey
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from binascii import hexlify
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    EccKeyType = Any
else:
    EccKeyType = EccKey


class TransactionSigner:

    @staticmethod
    def sign(private_key: EccKeyType, tx_hash: str) -> str: 
        
        hash_obj = SHA256.new(tx_hash.encode('utf-8'))
        signer = DSS.new(private_key, 'fips-186-3')  # type: ignore
        signature_bytes: bytes = signer.sign(hash_obj)
        signature_hex: str = hexlify(signature_bytes).decode('utf-8')
        return signature_hex