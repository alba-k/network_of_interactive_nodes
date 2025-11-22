# tools/client_transaction_builder.py
'''
Script: tools/client_transaction_builder.py
----------------------------------------------------------------------
Propósito: Simulación del CLIENTE (ESP32/Mobile).
Responsabilidad: Actuar como raíz de composición para los servicios del cliente.

*** CORRECCIÓN: Retorna objeto Response completo para validación HTTP. ***
----------------------------------------------------------------------
'''

import requests 
import time
import base64
import logging
import sys
import os
from typing import Optional

# 1. Truco para importar la librería 'core' y 'identity'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importaciones de Componentes y Núcleo Estático
from core.managers.wallet_manager import WalletManager 
from core.client_services.software_signer import SoftwareSigner 
from core.dto.api.data_submission import DataSubmission
from core.dto.data_entry_creation_params import DataEntryCreationParams
from core.factories.data_entry_factory import DataEntryFactory
from core.models.transaction import Transaction 
from identity.key_persistence import KeyPersistence 

# --- IMPORTACIÓN CLAVE: El Serializador que convierte Bytes -> Str ---
from core.serializers.transaction_serializer import TransactionSerializer

class ClientTransactionBuilder:

    def __init__(self, key_file_path: str = 'mi_billetera.pem', api_endpoint: str = "http://127.0.0.1:8000"):
        
        logging.info("Cliente App ensamblada...")
        
        # 1. Cargar la clave privada (Persistencia)
        private_key = KeyPersistence.ensure_key_exists(key_file_path)
        
        # 2. Composición: Crear el Adaptador de Firma
        self._signer = SoftwareSigner(private_key) 
        
        # 3. Composición: Crear el Wallet Manager
        # El WalletManager usará internamente el TransactionBuilder actualizado del Core
        self._wallet_manager = WalletManager(private_key.public_key(), self._signer) 

        self._api_endpoint = api_endpoint
        self._address = self._wallet_manager.get_address()
        
        logging.info(f"Cliente listo. Dirección: {self._address}")

    def get_address(self) -> str:
        return self._address

    # --- Lógica de Negocio ---

    def build_and_sign_transaction(self, submission: DataSubmission) -> Transaction:
        
        # 1. Decodificar el dato (value) de Base64 a bytes.
        value_bytes = base64.b64decode(submission.value) 
        
        # 2. Construir el DataEntry
        entry_params = DataEntryCreationParams(
            source_id=submission.source_id,
            data_type=submission.data_type,
            value=value_bytes,
            nonce=submission.nonce,
            metadata=submission.metadata
        )
        data_entry = DataEntryFactory.create(entry_params)
        
        # 3. Firmar la TX
        # Esto delegará al TransactionBuilder.build() del Core, que ya usa 
        # Firmas Deterministas y Hashing Binario. ¡Todo sincronizado!
        final_tx = self._wallet_manager.create_and_sign_data([data_entry])
            
        logging.info(f"TX firmada localmente: {final_tx.tx_hash[:6]}")
        return final_tx

    def submit_transaction(self, signed_tx: Transaction, api_url: str) -> Optional[requests.Response]:
        '''
        Envía la transacción al Gateway.
        Retorna el objeto Response crudo para que el BaseClient verifique el status_code.
        '''
        
        # 1. Serializar a Diccionario (Hex Strings)
        # Vital para que requests pueda convertirlo a JSON sin error de "bytes is not serializable"
        tx_data_dict = TransactionSerializer.to_dict(signed_tx)
        
        # 2. Crear el DTO de envío
        submission_payload = {'tx_data': tx_data_dict} 
        
        # 3. Enviar vía HTTP
        try:
            response = requests.post(
                f'{api_url}/submit_signed_tx',
                json=submission_payload,
                timeout=5
            )
            return response
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Fallo de conexión al Gateway: {e}")
            return None

# ... (El bloque if __name__ == "__main__": se mantiene igual para pruebas aisladas) ...
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    client = ClientTransactionBuilder(key_file_path='mi_billetera.pem')
    
    sensor_data = "40.5 C"
    raw_submission = DataSubmission(
        source_id=client.get_address(), 
        data_type="TEMPERATURA",
        value=base64.b64encode(sensor_data.encode('utf-8')).decode('utf-8'),
        nonce=int(time.time()),
        metadata={"unit": "C"}
    )
    
    try:
        final_tx = client.build_and_sign_transaction(raw_submission)
        logging.info(f"Prueba de firma local exitosa: {final_tx.tx_hash[:6]}")
    except Exception as e:
        logging.error(f"Error en prueba local: {e}")