# core/persistence/json/json_loader.py
'''
class JsonLoader:
    Herramienta especialista en LECTURA (Loading) para formato JSON.
'''

import json
import os
import logging
from typing import Optional
from core.models.blockchain import Blockchain
from core.deserializers.blockchain_deserializer import BlockchainDeserializer

class JsonLoader:

    def __init__(self, filepath: str):
        self._filepath = filepath

    def load(self) -> Optional[Blockchain]:
        # 1. Verificar existencia física
        if not os.path.exists(self._filepath):
            logging.warning(f"JsonLoader: Archivo '{self._filepath}' no encontrado. Se iniciará vacío.")
            return None

        try:
            # 2. Leer del disco
            with open(self._filepath, 'r') as f:
                data = json.load(f)
            
            # 3. Deserializar (Dict -> Objeto) usando el Núcleo Estático
            blockchain = BlockchainDeserializer.from_dict(data)
            
            logging.info(f"Persistencia: Blockchain cargada ({len(blockchain.chain)} bloques).")
            return blockchain

        except json.JSONDecodeError:
            logging.error(f"JsonLoader: El archivo '{self._filepath}' está corrupto (JSON inválido).")
            return None
        except Exception as e:
            logging.error(f"JsonLoader: Error fatal al leer/deserializar. {e}")
            return None