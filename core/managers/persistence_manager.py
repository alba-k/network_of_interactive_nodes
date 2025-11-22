
# core/managers/persistence_manager.py
'''
class PersistenceManager:
    El "Gerente" de almacenamiento.
    
    Responsabilidad:
        Abstraer la lógica de persistencia del resto del nodo.
        El nodo solo le dice "guarda", y el gerente usa la estrategia configurada.

    Attributes:
        _strategy (IPersistenceStrategy): La implementación concreta inyectada.
'''

import logging
from typing import Optional
from core.models.blockchain import Blockchain
from core.interfaces.i_persistence_strategy import IPersistenceStrategy

class PersistenceManager:

    def __init__(self, strategy: IPersistenceStrategy):
        # Inyección de Dependencias: El gerente recibe la herramienta a usar
        self._strategy = strategy
        logging.info(f"Persistence Manager inicializado (Estrategia: {type(strategy).__name__}).")

    def save_chain(self, blockchain: Blockchain) -> bool:
        logging.debug("Persistence: Solicitud de guardado recibida.")
        return self._strategy.save(blockchain)

    def load_chain(self) -> Optional[Blockchain]:
        logging.info("Persistence: Solicitud de carga recibida.")
        return self._strategy.load()