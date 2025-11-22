# identity/mnemonic_service.py
'''
class MnemonicService:
    Implementación del estándar BIP-39 para generar claves desde palabras humanas.
    
    *** CORRECCIÓN: Importa 'ECC' (módulo) en lugar de 'EccKey' para usar .construct() ***
'''

import hashlib
from mnemonic import Mnemonic
# [IMPORTANTE] Importamos el MÓDULO completo 'ECC', no solo la clase
from Crypto.PublicKey import ECC 

class MnemonicService:
    
    _LANGUAGE = 'english'
    
    @staticmethod
    def generate_new_mnemonic(strength: int = 128) -> str:
        mnemo = Mnemonic(MnemonicService._LANGUAGE)
        return mnemo.generate(strength=strength)

    @staticmethod
    def mnemonic_to_private_key(mnemonic_phrase: str, passphrase: str = "") -> ECC.EccKey:
        mnemo = Mnemonic(MnemonicService._LANGUAGE)
        
        if not mnemo.check(mnemonic_phrase):
            raise ValueError("La frase semilla es inválida.")

        seed_bytes = mnemo.to_seed(mnemonic_phrase, passphrase=passphrase)
        
        # Derivación simple (Seed -> SHA256 -> Private Key Integer)
        private_key_bytes = hashlib.sha256(seed_bytes).digest()
        private_key_int = int.from_bytes(private_key_bytes, 'big')
        
        # [CORRECCIÓN CRÍTICA]
        # Usamos ECC.construct (del módulo), NO EccKey.construct
        ecc_key = ECC.construct(curve='P-256', d=private_key_int)
        
        return ecc_key