# i_persistence_manager.py
'''
class IPersistenceManager(ABC):
    Define la Interfaz (Contrato) para un gestor de persistencia.

    Attributes:

    Methods:
        save(blockchain)->  None:                   Guarda el estado actual de la blockchain en el almacenamiento.
        load()->            Optional[Blockchain]:   Carga la blockchain desde el almacenamiento.
'''

from abc import ABC, abstractmethod # Importa helpers para crear Clases Abstractas (Interfaces)
from typing import Optional # Para type hints (indicar que algo puede ser 'None')
from core.models.blockchain import Blockchain # Importa el contenedor 'Blockchain' (el objeto a guardar/cargar)

class IPersistenceManager(ABC):
    
    @abstractmethod
    def save(self, blockchain: Blockchain) -> None:
        '''
        Guarda la cadena de bloques completa.
        Lanza excepciones si falla (ej. IOError).
        '''
        pass

    @abstractmethod
    def load(self) -> Optional[Blockchain]:
        '''
        Carga la cadena de bloques completa.
        Retorna la blockchain si la encuentra y es válida.
        Retorna None si no la encuentra o está corrupta.
        '''
        pass