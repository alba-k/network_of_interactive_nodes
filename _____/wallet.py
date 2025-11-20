# wallet.py
import time
import dataclasses
from typing import cast 

# Importamos y silenciamos el tipo para ecdsa 
from ecdsa import SigningKey, SECP256k1, VerifyingKey # type: ignore 
from core.models.transaction import Transaction 
from core.utils.crypto_utils import CryptoUtils # Usamos la clase CryptoUtils

class Wallet:
    _public_key_hex: str

    def __init__(self):
        # 1. Genera un par de llaves único al ser creada
        self._private_key = SigningKey.generate(curve = SECP256k1) # type: ignore
        
        # 2. Forzamos el tipo VerifyingKey con cast para eliminar el error 'None'
        self._public_key = cast(VerifyingKey, self._private_key.get_verifying_key()) # type: ignore
        
        # 3. El error 'to_string' se resuelve porque el linter confía en el tipo
        self._public_key_hex: str = self._public_key.to_string().hex() # type: ignore

    @property
    def public_key_hex(self) -> str:
        return self._public_key_hex

    def sign(self, data_hash: str) -> str:
        'Firma un hash (en formato hexadecimal) con la llave privada.'
        
        hash_bytes = bytes.fromhex(data_hash) 
        # Usamos CryptoUtils.sha256
        signature_bytes = self._private_key.sign(hash_bytes, hashfunc=CryptoUtils.sha256) # type: ignore
        
        return signature_bytes.hex() # type: ignore 

    def create_transaction(self, recipient_address: str, amount: float) -> Transaction:
        # ... (lógica de creación de transacción)
        tx_unsigned = Transaction(
            sender=self.public_key_hex,
            recipient=recipient_address,
            amount=amount,
            timestamp=time.time(),
            signature=None
        )
        tx_hash = tx_unsigned.calculate_hash()
        signature = self.sign(tx_hash)
        tx_signed = dataclasses.replace(tx_unsigned, signature=signature)
        return tx_signed