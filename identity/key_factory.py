# network_of_interactive_nodes/identity/key_factory.py
'''
class KeyFactory:
    Herramienta estática para la generación de claves criptográficas (ECC).
    
    Methods:
        generate_private_key() -> EccKey: Genera una nueva clave privada usando la curva NIST P-256.
'''

from Crypto.PublicKey import ECC
from Crypto.PublicKey.ECC import EccKey

class KeyFactory:

    @staticmethod
    def generate_private_key() -> EccKey:
        return ECC.generate(curve = 'P-256')