import logging
from typing import Dict, List, Tuple, Optional
from Crypto.PublicKey.ECC import EccKey
from core.nodes.full_node import FullNode
from core.managers.wallet_manager import WalletManager
from core.managers.api_manager import APIManager
from core.managers.mining_manager import MiningManager
from core.client_services.software_signer import SoftwareSigner 
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager
from core.managers.persistence_manager import PersistenceManager

class GatewayNode:
    def __init__(self, blockchain: Blockchain, consensus_manager: ConsensusManager, public_key_map: Dict[str, EccKey], mempool: Mempool, private_key: EccKey, host: str, port: int, api_host: str = "0.0.0.0", api_port: int = 8000, seed_peers: Optional[List[Tuple[str, int]]] = None, persistence_manager: Optional[PersistenceManager] = None):
        logging.info("Inicializando Gateway Node (Con soporte de Minería Remota)...")
        self._full_node = FullNode(blockchain=blockchain, consensus_manager=consensus_manager, public_key_map=public_key_map, mempool=mempool, host=host, port=port, seed_peers=seed_peers, persistence_manager=persistence_manager)
        self._signer = SoftwareSigner(private_key)
        self._wallet_manager = WalletManager(public_key=private_key.public_key(), signer=self._signer)
        self._mining_manager = MiningManager(miner_address=self._wallet_manager.get_address(), full_node=self._full_node)
        self._api_manager = APIManager(wallet_manager=self._wallet_manager, full_node=self._full_node, api_host=api_host, api_port=api_port, mining_manager=self._mining_manager)
        logging.info(f"Gateway Node ensamblado. API escuchando en {api_host}:{api_port}")

    async def start(self) -> None:
        logging.info(">>> ARRANCANDO GATEWAY NODE <<<")
        await self._full_node.start()
        self._api_manager.start_api_server()
        logging.info(">>> GATEWAY NODE OPERATIVO (Esperando comandos) <<<")

    async def stop(self) -> None:
        logging.info(">>> DETENIENDO GATEWAY NODE <<<")
        await self._mining_manager.stop_mining()
        self._api_manager.stop_api_server()
        await self._full_node.stop()
        logging.info(">>> GATEWAY NODE APAGADO <<<")
    
    def get_full_node(self) -> FullNode: return self._full_node
    def get_api_manager(self) -> APIManager: return self._api_manager
    def get_wallet_manager(self) -> WalletManager: return self._wallet_manager