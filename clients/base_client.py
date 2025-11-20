# clients/base_client.py
'''
class BaseClient:
    Clase base que encapsula la lógica común para clientes.

    Attributes:
        _builder     (ClientTransactionBuilder):    Herramienta compuesta para construir y firmar TXs.
        _gateway_url (str):                         URL del nodo Gateway al que se envían las transacciones.

    Methods:
        get_my_address() -> str: Retorna la dirección pública del cliente (ID).
        
        send_data(data_type: str, content_str: str, metadata: Optional[Dict]) -> bool: Orquesta el flujo de envío seguro.
            1. Empaquetar datos en DTO (DataSubmission).
            2. Firmar localmente (Delegar al Builder).
            3. Enviar por HTTP (Delegar al Builder).
'''

import sys
import os
import time
import base64
import logging
from typing import Dict, Any, Optional 

# Configuración de Imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.client_transaction_builder import ClientTransactionBuilder
from core.dto.api.data_submission import DataSubmission

class BaseClient:

    def __init__(self, key_file: str, gateway_url: str = 'http://127.0.0.1:8000'):
        logging.basicConfig(
            level = logging.INFO, 
            format = '[CLIENT] %(asctime)s - %(message)s', 
            datefmt = '%H:%M:%S'
        )
        
        logging.info(f'Iniciando Cliente Base con identidad: {key_file}')
        
        self._builder = ClientTransactionBuilder(key_file_path = key_file, api_endpoint = gateway_url)
        self._gateway_url = gateway_url
        
        logging.info(f'Cliente Conectado. ID: {self._builder.get_address()}')

    def get_my_address(self) -> str:
        return self._builder.get_address()

    def send_data(self, data_type: str, content_str: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        
        if metadata is None:
            metadata = {}

        try:
            submission = DataSubmission(
                source_id = self.get_my_address(),
                data_type = data_type,
                value=base64.b64encode(content_str.encode('utf-8')).decode('utf-8'),
                nonce=int(time.time()),
                metadata=metadata
            )

            signed_tx = self._builder.build_and_sign_transaction(submission)

            self._builder.submit_transaction(signed_tx, self._gateway_url)
            
            return True
            
        except Exception as e:
            logging.error(f'Error enviando datos: {e}')
            return False