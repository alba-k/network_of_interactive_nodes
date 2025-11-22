# core/persistence/strategies/json_strategy.py
'''
class JsonStrategy(IPersistenceStrategy):
    Implementación concreta de la estrategia JSON.
    
    Patrón: Composición.
    No hace el trabajo sucio; delega la escritura al JsonSaver y la lectura al JsonLoader.
'''

from typing import Optional
from core.models.blockchain import Blockchain
from core.interfaces.i_persistence_strategy import IPersistenceStrategy
from core.persistence.json.json_saver import JsonSaver
from core.persistence.json.json_loader import JsonLoader

class JsonStrategy(IPersistenceStrategy):

    def __init__(self, filepath: str = "blockchain_data.json"):
        self._filepath = filepath
        # Composición de especialistas
        self._saver = JsonSaver(filepath)
        self._loader = JsonLoader(filepath)

    def save(self, blockchain: Blockchain) -> bool:
        return self._saver.save(blockchain)

    def load(self) -> Optional[Blockchain]:
        return self._loader.load()