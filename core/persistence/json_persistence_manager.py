# json_persistence_manager.py
'''
class JsonPersistenceManager(IPersistenceManager):
    Especialista en leer y escribir el estado de la blockchain en un archivo JSON en disco.

    Attributes:
        _filename   (str):  Ruta y nombre del archivo JSON donde se guarda la cadena.

    Methods:
        save(blockchain)->  None:                   Serializa y guarda la cadena en el archivo JSON.
        load()->            Optional[Blockchain]:   Carga y valida la cadena desde el archivo JSON.
'''

import json # Para leer y escribir en formato JSON (guardar/cargar)
import logging # Para registrar eventos (ej. "guardado", "error al cargar")
from typing import Optional, List, Dict, Any # Para type hints (Listas, Diccionarios, etc.)
from core.models.blockchain import Blockchain # Importa el contenedor 'Blockchain' (el objeto a guardar/cargar)
import config # Importa la configuración (ej. nombre del archivo)
from core.serializers.block_serializer import BlockSerializer # Importa el "Traductor" (dict <-> objeto)
from core.persistence.i_persistence_manager import IPersistenceManager # Importa la Interfaz que implementa

class JsonPersistenceManager(IPersistenceManager):

    def __init__(self, filename: str = config.BLOCKCHAIN_FILE):
        self._filename: str = filename
        logging.info(f"Especialista de Persistencia JSON inicializado. \n\tArchivo: '{self._filename}'")

    def save(self, blockchain: Blockchain) -> None:
        '''
        Serializa y guarda la cadena completa en el archivo JSON.
        '''
        try:
            # --- Traductor ---
            chain_data: List[Dict[str, Any]] = BlockSerializer.blockchain_to_dict_list(blockchain)
            
            # --- Escribir en disco ---
            with open(self._filename, 'w') as f:
                json.dump(chain_data, f, indent=4)
            
            logging.info(f"Blockchain guardada (JSON) en '{self._filename}'.")
        
        except IOError as e:
            logging.error(f'Error Crítico: No se pudo guardar en JSON. {e}')
            raise
        except Exception as e:
            logging.error(f'Error inesperado al guardar JSON: {e}')
            raise

    def load(self) -> Optional[Blockchain]:
        '''
        Carga la blockchain desde el archivo JSON.
        '''
        chain_data: List[Dict[str, Any]]
        
        # --- Leer disco ---
        try:
            with open(self._filename, 'r') as f:
                chain_data = json.load(f)
        
        except (IOError, FileNotFoundError):
            # --- Archivo no encontrado (NORMAL) ---
            logging.warning(f"Archivo JSON '{self._filename}' no encontrado.\n\tSe creará una nueva blockchain.")
            return None
        except json.JSONDecodeError as e:
            # --- JSON corrupto (ERROR) ---
            logging.error(f"Archivo JSON '{self._filename}' corrupto. {e}")
            return None

        # --- Traductor ---
        try:
            blockchain: Blockchain = BlockSerializer.blockchain_from_dict_list(chain_data)
            
            logging.info(f"Blockchain cargada desde JSON '{self._filename}'.\n\tTotal: {len(blockchain.chain)} bloques.")
            return blockchain
        
        except (ValueError, KeyError, TypeError) as e:
            # --- Datos corruptos (CRÍTICO) ---
            logging.critical(f"DATOS CORRUPTOS en '{self._filename}'.\n\tEl hash no coincide o faltan claves. {e}")
            return None