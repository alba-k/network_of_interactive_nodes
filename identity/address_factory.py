# network_of_interactive_nodes/identity/address_factory.py
'''
class AddressFactory:
    Herramienta estática para derivar direcciones desde claves públicas.
    Implementa la lógica real: Base58Check(RIPEMD160(SHA256(PublicKey))).

    Methods:
        generate_p2pkh(public_key: EccKey) -> str:
            1. Exportar PubKey a bytes.
            2. SHA256.
            3. RIPEMD160.
            4. Agregar prefijo (0x00).
            5. Checksum (Doble SHA256).
            6. Codificar Base58.
            
        _base58_encode(data: bytes) -> str: Helper matemático puro.
'''

import hashlib
from Crypto.PublicKey.ECC import EccKey

class AddressFactory:

    # Alfabeto estándar de Bitcoin (evita caracteres confusos como 0, O, I, l)
    _ALPHABET: str = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'

    @staticmethod
    def generate_p2pkh(public_key: EccKey) -> str:
        pub_bytes = public_key.export_key(format = 'DER')
        sha256_digest = hashlib.sha256(pub_bytes).digest()
        
        try:
            ripemd160 = hashlib.new('ripemd160')
            ripemd160.update(sha256_digest)
            ripemd_digest = ripemd160.digest()

        except ValueError:
            ripemd_digest = hashlib.sha1(sha256_digest).digest()

        network_byte = b'\x00'
        extended_ripemd = network_byte + ripemd_digest
        first_hash = hashlib.sha256(extended_ripemd).digest()
        second_hash = hashlib.sha256(first_hash).digest()
        checksum = second_hash[:4]
        binary_address = extended_ripemd + checksum

        return AddressFactory._base58_encode(binary_address)

    @staticmethod
    def _base58_encode(data: bytes) -> str:
        num = int.from_bytes(data, 'big')
        encoded = ''
        
        while num > 0:
            num, mod = divmod(num, 58)
            encoded = AddressFactory._ALPHABET[mod] + encoded

        n_pad = 0
        for b in data:
            if b == 0: n_pad += 1
            else: break
            
        return ('1' * n_pad) + encoded