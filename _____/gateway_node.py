# network_of_interactive_nodes/core/nodes/gateway_node.py
'''
class GatewayNode(FullNode, IAPIRole, IWalletRole):
    Implementa un Nodo de la red que actúa como Gateway API y como FullNode P2P.
    
    Attributes:
        _private_key    (EccKey):           Clave privada de este nodo (para firmar).
        _public_key     (EccKey):           Clave pública derivada (para identidad).
        _api_host       (str):              Host para el servidor API (FastAPI).
        _api_port       (int):              Puerto para el servidor API.
        _app            (FastAPI):          Instancia de la aplicación FastAPI.
        _server_task    (asyncio.Task):     Tarea que ejecuta el servidor Uvicorn.
        (Hereda _blockchain, _consensus_manager, _mempool, _p2p_service de FullNode)
    
    Methods:
        start(): (Override) Inicia el P2P (padre) y el servidor API.
            1. Llama a FullNode.start()
            2. Llama a self.start_api_server()
        
        stop(): (Override) Detiene el P2P (padre) y el servidor API.
            1. Llama a FullNode.stop()
            2. Llama a self.stop_api_server()

        start_api_server(): (IAPIRole) Inicia el servidor Uvicorn (FastAPI) en una tarea.
        
        stop_api_server(): (IAPIRole) Detiene la tarea del servidor Uvicorn.

        handle_submit_data(submission): (IAPIRole) Manejador para el endpoint /submit_data.
            1. Deserializar (API DTO -> bytes)
            2. Crear DTO Interno (para el Factory)
            3. Delegar a "Herramienta" (DataEntryFactory)
            4. Delegar a "Wallet" (IWalletRole)
            5. Delegar a "FullNode" (Lógica P2P)

        create_and_sign_data(entries): (IWalletRole) Firma una lista de DataEntry.
            1. Crear sin firmar (para obtener el hash)
            2. Firmar (Delega a "Herramienta")
            3. Crear con firma (Delega a "Herramienta")
            4. FIRMA (Chequeo "Paranoico")
            5. Retornar la TX firmada.

        _setup_api_routes(): (Helper) Enlaza los endpoints de FastAPI a los manejadores.
'''

import logging
import time
import asyncio
import base64 
import uvicorn 
import binascii 
from fastapi import FastAPI, HTTPException
from typing import Dict, List, Tuple, Any, Optional
from Crypto.PublicKey.ECC import EccKey

# --- Importaciones de la Arquitectura ---
from core.nodes.full_node import FullNode
from core.interfaces.i_node_roles import IAPIRole, IWalletRole
from core.models.blockchain import Blockchain
from core.models.transaction import Transaction
from core.models.data_entry import DataEntry
from core.consensus.consensus_manager import ConsensusManager
from core.mempool.mempool import Mempool
from core.factories.transaction_factory import TransactionFactory
from core.factories.data_entry_factory import DataEntryFactory
from core.security.transaction_signer import TransactionSigner
from core.dto.transaction_creation_params import TransactionCreationParams
from core.dto.data_entry_creation_params import DataEntryCreationParams 
from core.dto.api.data_submission import DataSubmission
from core.utils.transaction_utils import TransactionUtils

class GatewayNode(FullNode, IAPIRole, IWalletRole):

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool,
                 private_key: EccKey,
                 api_host: str, 
                 api_port: int, 
                 host: str, 
                 port: int, 
                 seed_peers: Optional[List[Tuple[str, int]]] = None):
        
        FullNode.__init__(self, 
            blockchain, 
            consensus_manager, 
            public_key_map, 
            mempool, 
            host, 
            port, 
            seed_peers
        )
        
        self._private_key = private_key
        self._public_key = private_key.public_key()
        self._api_host = api_host
        self._api_port = api_port
        self._app = FastAPI()
        self._server_task: asyncio.Task[None] | None = None 
        self._setup_api_routes()
        
        logging.info(f'Gateway Node (API + P2P) inicializado. API en {api_host}:{api_port}')

    async def start(self):
        await FullNode.start(self)
        self.start_api_server()

    async def stop(self) -> None:
        await FullNode.stop(self)
        self.stop_api_server()
    
    def start_api_server(self):
        config = uvicorn.Config(self._app, host = self._api_host, port = self._api_port)
        server = uvicorn.Server(config)
        self._server_task = asyncio.create_task(server.serve())

    def stop_api_server(self):
        if self._server_task:
            self._server_task.cancel()
            
    def _setup_api_routes(self):
        self._app.post('/submit_data')(self.handle_submit_data)

    async def handle_submit_data(self, submission: DataSubmission) -> Dict[str, Any]:
        logging.info(f'API: Recibido /submit_data de {submission.source_id}')
        
        try:
            value_bytes = base64.b64decode(submission.value) 
            
            creation_params = DataEntryCreationParams(
                source_id = submission.source_id,
                data_type = submission.data_type,
                value = value_bytes, 
                nonce = submission.nonce,
                metadata = submission.metadata
            )
            
            entry = DataEntryFactory.create(params = creation_params)
            
            signed_tx = self.create_and_sign_data([entry])
            
            is_new = self.validate_tx_rules(signed_tx) 
            
            return {'status': 'recibido', 'tx_hash': signed_tx.tx_hash, 'is_new': is_new}
        
        except (binascii.Error, TypeError) as e: 
            logging.warning(f'API: Error decodificando Base64: {e}')
            raise HTTPException(status_code=400, detail="Base64 inválido")
        except Exception as e:
            logging.error(f'API: Error procesando /submit_data: {e}')
            raise HTTPException(status_code=500, detail=str(e))

    def create_and_sign_data(self, entries: List[DataEntry]) -> Transaction:

        current_timestamp: float = time.time()
        size_bytes: int = TransactionUtils.calculate_data_size(entries)
        
        params_no_sig = TransactionCreationParams(
            entries = entries, timestamp = current_timestamp, signature = None,
            fee = 0, size_bytes = size_bytes, fee_rate = 0.0
        )
        unsigned_tx: Transaction = TransactionFactory.create(params_no_sig)
        
        signature_hex: str = TransactionSigner.sign(
            private_key = self._private_key, 
            tx_hash = unsigned_tx.tx_hash
        )
        
        params_with_sig = TransactionCreationParams(
            entries = entries, 
            timestamp = current_timestamp, 
            signature = signature_hex,
            fee = 0,
            size_bytes = size_bytes, 
            fee_rate = 0.0
        )
        signed_tx: Transaction = TransactionFactory.create(params_with_sig)
        
        if signed_tx.tx_hash != unsigned_tx.tx_hash:
             raise RuntimeError('Error de firma: El Hash cambió (Gateway).')
             
        return signed_tx