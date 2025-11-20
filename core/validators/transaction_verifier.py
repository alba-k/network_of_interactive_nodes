# network_of_interactive_nodes/core/validators/transaction_verifier.py
'''
class TransactionVerifier:
    Contiene la lógica pura para verificar una firma de transacción usando el esquema ECDSA (Curva NIST P-256).

    Methods:
        verify(public_key: EccKey, tx_hash: str, signature_hex: str) -> bool: Verifica una firma de transacción.
            1. Hashear el hash de la transacción (tx_hash) con SHA-256.
            2. Convertir la firma (hex) de vuelta a bytes.
            3. Crear un verificador ECDSA (DSS) con la clave pública.
            4. Intentar verificar la firma contra el hash SHA-256.
            5. Retornar True si la verificación es exitosa.
            6. Retornar False si falla (ValueError o TypeError).
'''

from Crypto.PublicKey.ECC import EccKey
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from binascii import unhexlify

class TransactionVerifier:

    @staticmethod
    def verify(public_key: EccKey, tx_hash: str, signature_hex: str) -> bool:

        try:
            hash_obj = SHA256.new(tx_hash.encode('utf-8'))
            signature_bytes: bytes = unhexlify(signature_hex)
            verifier = DSS.new(public_key, 'fips-186-3')  # type: ignore
            verifier.verify(hash_obj, signature_bytes)
            return True

        except (ValueError, TypeError):
            return False