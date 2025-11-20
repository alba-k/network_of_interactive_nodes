# network_of_interactive_nodes/core/interfaces/i_key_loader.py
'''
class IKeyLoader(ABC):
    Define el contrato abstracto para cualquier clase que cargue claves (públicas o privadas).

    Methods:
        load(path: str) -> EccKey: Contrato para cargar una clave desde una ruta.
'''

from abc import ABC, abstractmethod
from Crypto.PublicKey.ECC import EccKey

class IKeyLoader(ABC):

    @staticmethod
    @abstractmethod
    def load(path: str) -> EccKey:
        pass