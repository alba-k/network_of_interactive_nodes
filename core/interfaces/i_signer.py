# core/interfaces/i_signer.py
'''
class ISigner(ABC):
    Define el contrato para cualquier objeto capaz de realizar una firma ECDSA.
    
    Este puerto permite inyectar una llave de hardware, un servicio en la nube 
    o una llave local sin modificar el WalletManager.
    
    Methods:
        sign(tx_hash: str) -> str: Contrato para firmar un hash de transacción.
'''

from abc import ABC, abstractmethod

class ISigner(ABC):
    
    @abstractmethod
    def sign(self, tx_hash: str) -> str:
        """Firma un hash de transacción y retorna el string hexadecimal de la firma."""
        pass