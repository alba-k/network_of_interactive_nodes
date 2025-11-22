# core/interfaces/i_persistence_strategy.py
'''
class IPersistenceStrategy(ABC):
    Define el Contrato (Interfaz) para una estrategia de almacenamiento.
    
    No es un "Manager", es una definición de capacidades que cualquier 
    formato (JSON, SQL, LevelDB) debe cumplir.

    Methods:
        save(blockchain) -> bool: Guardar estado.
        load() -> Blockchain: Cargar estado.
'''

from abc import ABC, abstractmethod
from typing import Optional
from core.models.blockchain import Blockchain

class IPersistenceStrategy(ABC):
    
    @abstractmethod
    def save(self, blockchain: Blockchain) -> bool:
        pass

    @abstractmethod
    def load(self) -> Optional[Blockchain]:
        pass