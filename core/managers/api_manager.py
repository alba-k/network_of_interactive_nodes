# core/managers/api_manager.py
'''
class APIManager(IAPIRole):
    Implementa el "Rol" de API Gateway (Servidor Web).
    
    Su responsabilidad es levantar un servidor FastAPI (Uvicorn) y exponer endpoints
    que permitan al mundo exterior interactuar con la Blockchain.

    Endpoints:
        POST /submit_data: Para clientes simples. El nodo firma con su WalletManager.
        POST /submit_signed_tx: Para clientes IoT (ESP32). El nodo solo retransmite.
        GET /health: Estado del nodo.

    Attributes:
        _wallet_manager (WalletManager): Gestor de firma (Inyectado).
        _full_node (FullNode): Contenedor principal (Inyectado).
        _app (FastAPI): Aplicación web.
        _server_task (Task): Tarea de fondo para el servidor.
'''

import logging
import asyncio
import base64 
import uvicorn 
from fastapi import FastAPI, HTTPException
from typing import Dict, Any

# Interfaces y Componentes
from core.interfaces.i_node_roles import IAPIRole
from core.managers.wallet_manager import WalletManager
from core.nodes.full_node import FullNode

# DTOs y Modelos
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
        logging.info(f'API Manager configurado. Listo para iniciar en http://{api_host}:{api_port}')

    # --- Implementación de IAPIRole (Ciclo de Vida) ---

    def start_api_server(self):
        # Configurar Uvicorn
        config = uvicorn.Config(self._app, host=self._api_host, port=self._api_port, log_level="info")
        server = uvicorn.Server(config)
        
        # Iniciar en background para no bloquear el P2P
        self._server_task = asyncio.create_task(server.serve())
        logging.info(f'API Server corriendo en segundo plano.')

    def stop_api_server(self):
        if self._server_task:
            logging.info("Deteniendo API Server...")
            self._server_task.cancel()

    # --- Rutas y Endpoints ---

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

    # --- Handlers (Lógica de Endpoints) ---

    async def handle_submit_data(self, submission: DataSubmission) -> Dict[str, Any]:
        '''Caso 1: Cliente Web (El Nodo firma).'''
        logging.info(f'API: Recibido dato crudo de {submission.source_id}')
        try:
            # 1. Decodificar y Crear DataEntry
            value_bytes = base64.b64decode(submission.value) 
            creation_params = DataEntryCreationParams(
                source_id=submission.source_id,
                data_type=submission.data_type,
                value=value_bytes, 
                nonce=submission.nonce,
                metadata=submission.metadata
            )
            entry = DataEntryFactory.create(params=creation_params)
            
            # 2. FIRMAR (Usando el WalletManager del Gateway)
            signed_tx = self._wallet_manager.create_and_sign_data([entry])
            
            # 3. Validar y Propagar (Usando el FullNode)
            is_accepted = self._full_node.get_validation_manager().validate_tx_rules(signed_tx) 
            
            # 4. Forzar broadcast si es válida (Doble seguridad)
            if is_accepted:
                self._full_node.get_p2p_manager().broadcast_new_tx(signed_tx)

            return {'status': 'broadcasted', 'tx_hash': signed_tx.tx_hash}
        
        except Exception as e:
            logging.error(f'API Error: {e}')
            raise HTTPException(status_code=400, detail=str(e))

    async def handle_submit_signed_tx(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        '''Caso 2: Cliente IoT (Ya viene firmado).'''
        logging.info(f'API: Recibida TX firmada externamente.')
        try:
            tx_data = submission.get('tx_data')
            if not tx_data:
                raise ValueError("Falta 'tx_data' en el cuerpo del request.")

            # 1. Reconstruir la transacción (Deserializar)
            #    Aquí usamos el Núcleo Estático para convertir JSON -> Objeto
            tx_obj = TransactionDeserializer.from_dict(tx_data)

            # 2. Validar Reglas y Firmas (Usando el FullNode)
            #    Esto verifica criptográficamente que el ESP32 firmó bien.
            validation_manager = self._full_node.get_validation_manager()
            is_valid = validation_manager.validate_tx_rules(tx_obj)

            if is_valid:
                # 3. Propagar a la red P2P
                self._full_node.get_p2p_manager().broadcast_new_tx(tx_obj)
                return {'status': 'relayed', 'tx_hash': tx_obj.tx_hash}
            else:
                raise ValueError("TX rechazada: Firma inválida o duplicada.")

        except Exception as e:
            logging.error(f'API Relay Error: {e}')
            raise HTTPException(status_code=400, detail=str(e))