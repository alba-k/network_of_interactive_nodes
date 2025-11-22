# network_of_interactive_nodes/core/persistence/json/json_saver.py
'''
class JsonSaver:
    Especialista en ESCRITURA (Saving) para formato JSON.
    Implementa el patrón "Atomic Write" para garantizar la integridad de datos ante fallos de energía o crash.

    Methods:
        save(blockchain: Blockchain) -> bool:
            1. Serializar la blockchain a diccionario.
            2. Crear un archivo temporal seguro.
            3. Escribir y forzar sincronización en disco (fsync).
            4. Reemplazar atómicamente el archivo destino.
'''

import json
import logging
import os
import tempfile

# Importaciones de la Arquitectura
from core.models.blockchain import Blockchain
from core.serializers.blockchain_serializer import BlockchainSerializer

class JsonSaver:

    def __init__(self, filepath: str):
        self._filepath = filepath

    def save(self, blockchain: Blockchain) -> bool:
        temp_fd = None
        temp_path = None

        try:
            chain_dict = BlockchainSerializer.to_dict(blockchain)
            directory = os.path.dirname(self._filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            temp_fd, temp_path = tempfile.mkstemp(dir=directory, text=True)

            with os.fdopen(temp_fd, 'w') as tmp_file:
                json.dump(chain_dict, tmp_file, indent=4)
                tmp_file.flush()
                os.fsync(tmp_file.fileno())
            
            temp_fd = None 

            os.replace(temp_path, self._filepath)

            logging.info(f'''Persistencia: Blockchain guardada de forma atómica en '{self._filepath}'.''')
            return True

        except Exception as e:
            logging.error(f'''JsonSaver: Error crítico al guardar (Atomic Write falló). {e}''')
            
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            return False
            
        finally:
            if temp_fd:
                try:
                    os.close(temp_fd)
                except OSError:
                    pass