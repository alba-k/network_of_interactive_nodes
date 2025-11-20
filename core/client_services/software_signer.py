# core/client_services/software_signer.py
'''
class SoftwareSigner(ISigner):
    Adaptador (Adapter) que implementa el contrato ISigner (firma) 
    para una clave cargada localmente (en software/memoria).
    
    Responsabilidad: Realizar la operación criptográfica real usando la clave que le fue inyectada.

    Attributes:
        _private_key (EccKey): La clave privada (guardada temporalmente en memoria).

    Methods:
        sign(tx_hash: str) -> str: Delega la firma al TransactionSigner (Núcleo Estático).
'''

import logging
from Crypto.PublicKey.ECC import EccKey

# Interfaces
from core.interfaces.i_signer import ISigner

# Núcleo Estático (El que sabe de criptografía)
from core.security.transaction_signer import TransactionSigner

class SoftwareSigner(ISigner):

    def __init__(self, private_key: EccKey):
        # 1. El adaptador recibe la clave que fue cargada/generada por el cliente.
        self._private_key = private_key
        logging.info("Signer de software inicializado con clave local (Adapter listo).")

    def sign(self, tx_hash: str) -> str:
        # 1. Verificar si la clave existe.
        if not self._private_key:
            raise RuntimeError("Cannot sign: Private key not available in software signer.")
            
        # 2. Delegar la operación criptográfica real a la herramienta estática.
        return TransactionSigner.sign(self._private_key, tx_hash)