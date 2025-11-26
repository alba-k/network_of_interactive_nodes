# core/managers/api_manager.py (VERSIÓN FINAL - CORRECCIÓN DE FIRMA IOT)
'''
class APIManager(IAPIRole):
    Implementa el "Rol" de API Gateway.
    SOLUCIÓN DE FIRMA: Cuando recibe datos de un sensor sin wallet (ESP32),
    el Gateway firma la transacción con SU propia wallet y se registra como el 'source_id',
    guardando el ID original del sensor en los metadatos.
'''

import logging
import asyncio
import base64 
import uvicorn 
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

from core.interfaces.i_node_roles import IAPIRole
from core.managers.wallet_manager import WalletManager
from core.nodes.full_node import FullNode
from core.dto.api.data_submission import DataSubmission
from core.dto.data_entry_creation_params import DataEntryCreationParams
from core.factories.data_entry_factory import DataEntryFactory
from core.deserializers.transaction_deserializer import TransactionDeserializer

class APIManager(IAPIRole):

    def __init__(self, 
                 wallet_manager: WalletManager, 
                 full_node: FullNode,         
                 api_host: str = "0.0.0.0", 
                 api_port: int = 8000):
        
        self._wallet_manager = wallet_manager
        self._full_node = full_node
        self._api_host = api_host
        self._api_port = api_port
        self._app = FastAPI(title="Blockchain Gateway Node")
        self._server_task: asyncio.Task[None] | None = None 
        self._setup_api_routes()
        logging.info(f'API Manager listo en http://{api_host}:{api_port}')

    def start_api_server(self):
        config = uvicorn.Config(self._app, host=self._api_host, port=self._api_port, log_level="info")
        server = uvicorn.Server(config)
        self._server_task = asyncio.create_task(server.serve())
        logging.info(f'API Server corriendo en segundo plano.')

    def stop_api_server(self):
        if self._server_task:
            logging.info("Deteniendo API Server...")
            self._server_task.cancel()

    def _setup_api_routes(self):
        self._app.post('/submit_data')(self.handle_submit_data)
        self._app.post('/submit_signed_tx')(self.handle_submit_signed_tx)
        self._app.get('/health')(self._get_health_status)

    def _get_health_status(self) -> Dict[str, Any]:
        blockchain = self._full_node.get_blockchain()
        mempool = self._full_node.get_mempool()
        last_block = blockchain.last_block
        return {
            "status": "online", 
            "role": "GATEWAY",
            "height": last_block.index if last_block else 0,
            "mempool_size": mempool.get_transaction_count(),
            "address": self._wallet_manager.get_address()
        }

    async def handle_submit_data(self, submission: DataSubmission) -> Dict[str, Any]:
        '''Caso 1: Cliente IoT (El Gateway firma por él).'''
        logging.info(f'API: Procesando dato de sensor: {submission.source_id}')
        try:
            # 1. TRUCO DE SEGURIDAD: 
            # Usamos la dirección del Gateway como 'source_id' porque es quien tiene la llave privada.
            signer_address = self._wallet_manager.get_address()

            # 2. PRESERVAR DATOS:
            # Guardamos el ID real del sensor en los metadatos.
            final_metadata = submission.metadata if submission.metadata else {}
            final_metadata['original_sensor_id'] = submission.source_id
            final_metadata['data_type_original'] = submission.data_type

            # 3. Decodificar
            value_bytes = base64.b64decode(submission.value) 

            # 4. Crear DataEntry (A nombre del Gateway)
            creation_params = DataEntryCreationParams(
                source_id=signer_address,  # <--- CAMBIO CRÍTICO AQUÍ
                data_type="IOT_DELEGATED", # Tipo genérico para datos delegados
                value=value_bytes, 
                nonce=submission.nonce,
                metadata=final_metadata
            )
            entry = DataEntryFactory.create(params=creation_params)
            
            # 5. Firmar
            signed_tx = self._wallet_manager.create_and_sign_data([entry])
            
            # 6. Validar y Propagar
            # Ahora pasará la validación porque (Firma == Source_ID)
            validation_manager = self._full_node.get_validation_manager()
            
            if validation_manager.validate_tx_rules(signed_tx):
                self._full_node.get_p2p_manager().broadcast_new_tx(signed_tx)
                logging.info(f"✅ API: Transacción aceptada y propagada ({signed_tx.tx_hash[:8]})")
                return {'status': 'broadcasted', 'tx_hash': signed_tx.tx_hash}
            else:
                logging.warning("API: Transacción rechazada por reglas de consenso internas.")
                raise ValueError("Fallo de validación interna.")
        
        except Exception as e:
            logging.error(f'API Error: {e}')
            raise HTTPException(status_code=400, detail=str(e))

    async def handle_submit_signed_tx(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        '''Caso 2: Cliente IoT Avanzado (Ya viene firmado).'''
        try:
            tx_data = submission.get('tx_data')
            if not tx_data: raise ValueError("Falta 'tx_data'.")

            tx_obj = TransactionDeserializer.from_dict(tx_data)
            validation_manager = self._full_node.get_validation_manager()
            
            if validation_manager.validate_tx_rules(tx_obj):
                self._full_node.get_p2p_manager().broadcast_new_tx(tx_obj)
                return {'status': 'relayed', 'tx_hash': tx_obj.tx_hash}
            else:
                raise ValueError("Firma inválida.")
        except Exception as e:
            logging.error(f'API Relay Error: {e}')
            raise HTTPException(status_code=400, detail=str(e))