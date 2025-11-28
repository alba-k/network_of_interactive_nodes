import logging
import asyncio
import base64 
import uvicorn 
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, List, Optional
from core.interfaces.i_node_roles import IAPIRole
from core.managers.wallet_manager import WalletManager
from core.nodes.full_node import FullNode
from core.dto.api.data_submission import DataSubmission
from core.dto.data_entry_creation_params import DataEntryCreationParams
from core.factories.data_entry_factory import DataEntryFactory
from core.deserializers.transaction_deserializer import TransactionDeserializer
from core.managers.mining_manager import MiningManager

class APIManager(IAPIRole):

    def __init__(self, wallet_manager: WalletManager, full_node: FullNode, api_host: str = "0.0.0.0", api_port: int = 8000, mining_manager: Optional[MiningManager] = None):
        self._wallet_manager = wallet_manager
        self._full_node = full_node
        self._mining_manager = mining_manager
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
        self._app.get('/api/chain')(self._get_chain_data)
        self._app.get('/api/mempool')(self._get_mempool_data)
        self._app.get('/api/peers')(self._get_peers_data)
        self._app.post('/api/control/mining/start')(self._start_mining_cmd)
        self._app.post('/api/control/mining/stop')(self._stop_mining_cmd)

    def _get_health_status(self) -> Dict[str, Any]:
        blockchain = self._full_node.get_blockchain()
        mempool = self._full_node.get_mempool()
        is_mining = False
        if self._mining_manager: is_mining = self._mining_manager.is_mining_active()
        return {"status": "online", "role": "MINER" if is_mining else "GATEWAY", "height": blockchain.last_block.index if blockchain.last_block else 0, "mempool_size": mempool.get_transaction_count(), "address": self._wallet_manager.get_address()}

    async def handle_submit_data(self, submission: DataSubmission) -> Dict[str, Any]:
        try:
            value_bytes = base64.b64decode(submission.value) 
            signer_addr = self._wallet_manager.get_address()
            meta = submission.metadata if submission.metadata else {}
            meta['original_sensor'] = submission.source_id
            creation_params = DataEntryCreationParams(source_id=signer_addr, data_type="IOT_DELEGATED", value=value_bytes, nonce=submission.nonce, metadata=meta)
            entry = DataEntryFactory.create(params=creation_params)
            signed_tx = self._wallet_manager.create_and_sign_data([entry])
            validation_manager = self._full_node.get_validation_manager()
            if validation_manager.validate_tx_rules(signed_tx):
                p2p = self._full_node.get_p2p_manager()
                if asyncio.iscoroutinefunction(p2p.broadcast_new_tx): await p2p.broadcast_new_tx(signed_tx)
                else: p2p.broadcast_new_tx(signed_tx)
                return {'status': 'broadcasted', 'tx_hash': signed_tx.tx_hash}
            raise ValueError("Fallo de validación interna.")
        except Exception as e: raise HTTPException(status_code=400, detail=str(e))

    async def handle_submit_signed_tx(self, submission: Dict[str, Any]) -> Dict[str, Any]:
        try:
            tx_data = submission.get('tx_data')
            if not tx_data: raise ValueError("Falta 'tx_data'.")
            tx_obj = TransactionDeserializer.from_dict(tx_data)
            validation_manager = self._full_node.get_validation_manager()
            if validation_manager.validate_tx_rules(tx_obj):
                p2p = self._full_node.get_p2p_manager()
                if asyncio.iscoroutinefunction(p2p.broadcast_new_tx): await p2p.broadcast_new_tx(tx_obj)
                else: p2p.broadcast_new_tx(tx_obj)
                return {'status': 'relayed', 'tx_hash': tx_obj.tx_hash}
            raise ValueError("Firma inválida.")
        except Exception as e: raise HTTPException(status_code=400, detail=str(e))

    def _get_chain_data(self) -> Dict[str, Any]:
        bc = self._full_node.get_blockchain()
        chain_list = bc.chain
        latest: List[Dict[str, Any]] = []
        for b in chain_list[-10:][::-1]:
            miner = "Genesis"
            if b.data and b.data[0].entries: miner = b.data[0].entries[0].source_id
            latest.append({"index": b.index, "hash": b.hash, "miner": miner, "tx_count": len(b.data), "timestamp": b.timestamp})
        return {"length": len(chain_list), "latest_blocks": latest}

    def _get_mempool_data(self) -> Dict[str, Any]:
        mp = self._full_node.get_mempool()
        txs = mp.get_transactions_for_block(50)
        t_list: List[Dict[str, Any]] = []
        for t in txs:
            if t.entries: t_list.append({"tx_hash": t.tx_hash, "type": t.entries[0].data_type, "source": t.entries[0].source_id})
        return {"count": len(t_list), "transactions": t_list}

    def _get_peers_data(self) -> Dict[str, Any]:
        p2p = self._full_node.get_p2p_manager()
        count = 0
        if hasattr(p2p, '_p2p_service'):
            svc = getattr(p2p, '_p2p_service')
            if hasattr(svc, '_peers'): count = len(getattr(svc, '_peers'))
        return {"peers_count": count}

    async def _start_mining_cmd(self) -> Dict[str, str]:
        if self._mining_manager:
            logging.info("API: Recibida orden de INICIAR minería.")
            await self._mining_manager.start_mining()
            return {"status": "success", "message": "Minería INICIADA"}
        return {"status": "error", "message": "Este nodo no tiene capacidad de minería"}

    async def _stop_mining_cmd(self) -> Dict[str, str]:
        if self._mining_manager:
            logging.info("API: Recibida orden de DETENER minería.")
            await self._mining_manager.stop_mining()
            return {"status": "success", "message": "Minería DETENIDA"}
        return {"status": "error", "message": "Este nodo no tiene capacidad de minería"}