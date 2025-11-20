# sqlite_persistence_manager.py

import logging # Para registrar eventos (ej. "Nodo iniciado", "Error")
from typing import Optional # Para type hints (indicar que algo puede ser 'None')
from core.models.blockchain import Blockchain # Importa el contenedor 'Blockchain'
from core.persistence.i_persistence_manager import IPersistenceManager # Importa la Interfaz de persistencia
import config # Importa la configuración global (ej. Puerto, Dificultad)

class SqlitePersistenceManager(IPersistenceManager):
    '''
    Esqueleto para el especialista en persistencia SQLite.
    '''

    def __init__(self, db_name: str = getattr(config, 'SQLITE_DB_FILE', 'blockchain_data.db')):
        
        self._db_name: str = db_name
        logging.info(f"Especialista SQLite (Stub) inicializado. DB: '{self._db_name}'")
        #
        # (Aquí iría la llamada a self._create_tables() en el futuro)
        #

    def save(self, blockchain: Blockchain) -> None:
        '''
        (FUTURA IMPLEMENTACIÓN)
        Guarda la cadena completa en la DB SQLite.
        '''
        logging.warning(f"Método 'save' NO IMPLEMENTADO para SqlitePersistenceManager.")
        pass

    def load(self) -> Optional[Blockchain]:
        '''
        (FUTURA IMPLEMENTACIÓN)
        Carga la cadena completa desde la DB SQLite.
        '''
        logging.warning(f"Método 'load' NO IMPLEMENTADO para SqlitePersistenceManager.")
        return None