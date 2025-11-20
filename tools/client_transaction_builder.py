'''
Script: tools/client_transaction_builder.py
----------------------------------------------------------------------
Propósito: Simulación del CLIENTE (ESP32/Mobile). Demuestra el flujo de 
           generación de datos, firma LOCAL y envío a la API del Gateway.

Responsabilidad: Actuar como raíz de composición para los servicios del cliente.
----------------------------------------------------------------------
'''

import requests 
import time
import base64
import logging
import sys
import os
import dataclasses

# 1. Truco para importar la librería 'core' y 'identity'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importaciones de Componentes y Núcleo Estático
from core.managers.wallet_manager import WalletManager 
from core.client_services.software_signer import SoftwareSigner 
from core.dto.api.data_submission import DataSubmission
from core.dto.data_entry_creation_params import DataEntryCreationParams # <--- CORREGIDO
from core.factories.data_entry_factory import DataEntryFactory
from core.models.transaction import Transaction 
from identity.key_persistence import KeyPersistence 

class ClientTransactionBuilder:

    def __init__(self, key_file_path: str = 'mi_billetera.pem', api_endpoint: str = "http://127.0.0.1:8000"):
        
        logging.info("Cliente App ensamblada...")
        
        # 1. Cargar la clave privada (Persistencia)
        private_key = KeyPersistence.ensure_key_exists(key_file_path)
        
        # 2. Composición: Crear el Adaptador de Firma (Polimorfismo)
        self._signer = SoftwareSigner(private_key) 
        
        # 3. Composición: Crear el Wallet Manager (Lógica de Address/TX)
        self._wallet_manager = WalletManager(private_key.public_key(), self._signer) 

        self._api_endpoint = api_endpoint
        # La dirección se obtiene a través del gestor, no se almacena como atributo interno
        
        logging.info(f"Cliente listo. Dirección: {self._wallet_manager.get_address()}")

    # --- Nuevo Getter (Soluciona el error de la imagen) ---
    def get_address(self) -> str:
        '''Expone la dirección pública del wallet de forma controlada.'''
        return self._wallet_manager.get_address()

    # --- Lógica de Negocio (El Corazón del Cliente) ---

    def build_and_sign_transaction(self, submission: DataSubmission) -> Transaction:
        # 1. Decodificar el dato (value) de Base64 a bytes.
        value_bytes = base64.b64decode(submission.value) 
        
        # 2. Construir el DataEntry (Átomo de la transacción).
        entry_params = DataEntryCreationParams(
            source_id=submission.source_id,
            data_type=submission.data_type,
            value=value_bytes,
            nonce=submission.nonce,
            metadata=submission.metadata
        )
        data_entry = DataEntryFactory.create(entry_params)
        
        # 3. Firmar la TX (Delegamos al WalletManager, que usará el SoftwareSigner).
        final_tx = self._wallet_manager.create_and_sign_data([data_entry])
            
        logging.info(f"TX firmada localmente: {final_tx.tx_hash[:6]}")
        return final_tx

    def submit_transaction(self, signed_tx: Transaction, api_url: str):
        # 1. Serializar la Transacción Firmada a un diccionario (JSON-friendly).
        tx_data_dict = dataclasses.asdict(signed_tx)
        
        # 2. Crear el DTO de envío para el Gateway.
        submission_payload = {'tx_data': tx_data_dict} 
        
        # 3. Enviar vía HTTP (Usando el endpoint /submit_signed_tx).
        try:
            response = requests.post(
                f'{api_url}/submit_signed_tx',
                json=submission_payload,
                timeout=5
            )
            response.raise_for_status()
            logging.info(f"TX enviada. Respuesta del Gateway: {response.json().get('status')}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Fallo de conexión al Gateway: {e}")
            raise

# --- EJEMPLO DE USO (El "firmware" ejecutándose) ---

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    
    # 1. Inicializar el Cliente Constructor (Composition Root)
    client = ClientTransactionBuilder(key_file_path='mi_billetera.pem')
    
    # 2. El ESP32 toma una lectura (ej. temperatura)
    sensor_data = "40.5 C"
    
    # 3. Construye el DTO de datos (Lo que genera el ESP32)
    raw_submission = DataSubmission(
        # CORREGIDO: Usamos el método getter
        source_id=client.get_address(), 
        data_type="TEMPERATURA",
        value=base64.b64encode(sensor_data.encode('utf-8')).decode('utf-8'),
        nonce=int(time.time()),
        metadata={"unit": "C"}
    )
    
    # 4. Construir y Firmar la Transacción (Todo ocurre en el dispositivo cliente)
    final_tx = client.build_and_sign_transaction(raw_submission)
    
    logging.info(f"Cliente (ESP32) ha completado la firma local para {final_tx.tx_hash[:6]}.")
    
    # 5. Enviar la Transacción Firmada al Servidor Gateway (API)
    # Nota: Descomentar la siguiente sección para probar si el GatewayNode está corriendo en el puerto 8000
    # try:
    #     client.submit_transaction(final_tx, client._api_endpoint)
    # except Exception:
    #     logging.error("No se pudo enviar la TX. Asegúrese de que el GatewayNode esté activo en 127.0.0.1:8000.")