# clients/base_client.py
'''
class BaseClient:
    Clase base que encapsula la lógica común para clientes.

    *** ACTUALIZACIÓN: Validación de respuesta HTTP (Status Code). ***

    Attributes:
        _builder     (ClientTransactionBuilder):    Herramienta compuesta para construir y firmar TXs.
        _gateway_url (str):                         URL del nodo Gateway.

    Methods:
        get_my_address() -> str: Retorna la dirección pública del cliente (ID).
        send_data(...) -> bool: Orquesta el flujo de envío seguro y verifica éxito.
'''

import sys
import os
import time
import base64
import logging
# Necesario para tipado de Response (opcional, pero bueno para catch)
from typing import Dict, Any, Optional 

# Configuración de Imports Robusta
# Añade la raíz del proyecto para encontrar 'tools' y 'core'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from tools.client_transaction_builder import ClientTransactionBuilder
from core.dto.api.data_submission import DataSubmission

class BaseClient:

    def __init__(self, key_file: str, gateway_url: str = 'http://127.0.0.1:8000'):
        # Configuración de logging básica si no existe
        if not logging.getLogger().hasHandlers():
            logging.basicConfig(
                level = logging.INFO, 
                format = '[CLIENT] %(asctime)s - %(message)s', 
                datefmt = '%H:%M:%S'
            )
        
        logging.info(f'Iniciando Cliente Base con identidad: {key_file}')
        
        # Delegamos la criptografía al Builder
        self._builder = ClientTransactionBuilder(key_file_path = key_file, api_endpoint = gateway_url)
        self._gateway_url = gateway_url
        
        logging.info(f'Cliente Conectado. ID: {self._builder.get_address()}')

    def get_my_address(self) -> str:
        return self._builder.get_address()

    def send_data(self, data_type: str, content_str: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
        
        if metadata is None:
            metadata = {}

        try:
            # 1. Preparar el DTO de envío
            submission = DataSubmission(
                source_id = self.get_my_address(),
                data_type = data_type,
                # Codificamos en Base64 para transmisión segura HTTP
                value=base64.b64encode(content_str.encode('utf-8')).decode('utf-8'),
                nonce=int(time.time()),
                metadata=metadata
            )

            # 2. Construir y Firmar (Aquí ocurre la magia criptográfica)
            signed_tx = self._builder.build_and_sign_transaction(submission)

            # 3. Enviar por HTTP y VERIFICAR RESPUESTA
            response = self._builder.submit_transaction(signed_tx, self._gateway_url)
            
            # [FIX] Verificación de Código de Estado
            if response and response.status_code == 200:
                return True
            else:
                logging.warning(f"Envío fallido. Code: {response.status_code if response else 'No Response'}. Body: {response.text if response else ''}")
                return False
            
        except Exception as e:
            logging.error(f'Excepción enviando datos: {e}')
            return False