# network_of_interactive_nodes/core/nodes/miner_node.py
'''
class MinerNode:
    Fachada (Facade) que representa un Nodo Minero listo para usar.
    
    No contiene lógica de negocio. Su responsabilidad es la COMPOSICIÓN:
    Ensambla un FullNode y le conecta un MiningManager.

    Cumple la definición: "Full Node + Software de Minería".

    Attributes:
        _full_node (FullNode): La instancia del nodo base (P2P, Validación).
        _mining_manager (MiningManager): El servicio que realiza el trabajo de minería.

    Methods:
        start(): Inicia el nodo y luego el minero.
        stop(): Detiene el minero y luego el nodo.
        get_full_node(): Acceso al nodo interno.
'''

import logging
from typing import Dict, List, Tuple, Optional, Any
from Crypto.PublicKey.ECC import EccKey

# Importaciones de Componentes
from core.nodes.full_node import FullNode
from core.managers.mining_manager import MiningManager

# Importaciones de Modelos Base (Para el constructor)
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

class MinerNode:

    def __init__(self, 
                 miner_address: str,
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool, 
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None,
                 persistence_manager: Any = None):
        
        logging.info(f"Inicializando Miner Node para: {miner_address}")

        # 1. Instanciar el "Full Node" (El Motor)
        self._full_node = FullNode(
            blockchain=blockchain,
            consensus_manager=consensus_manager,
            public_key_map=public_key_map,
            mempool=mempool,
            host=host,
            port=port,
            seed_peers=seed_peers,
            persistence_manager=persistence_manager
        )

        # 2. Instanciar el "Software de Minería" (El Trabajador)
        #    Le pasamos el nodo para que pueda acceder al Mempool y P2P.
        self._mining_manager = MiningManager(
            miner_address=miner_address,
            full_node=self._full_node
        )
        
        logging.info("Miner Node ensamblado correctamente.")

    async def start(self) -> None:
        logging.info(">>> ARRANCANDO MINER NODE <<<")
        
        # 1. Arrancar el Nodo Base (Red y Validación)
        await self._full_node.start()
        
        # 2. Arrancar el Minero
        await self._mining_manager.start_mining()
        
        logging.info(">>> MINER NODE OPERATIVO <<<")

    async def stop(self) -> None:
        logging.info(">>> DETENIENDO MINER NODE <<<")
        
        # 1. Parar Minería primero (dejar de crear bloques)
        await self._mining_manager.stop_mining()
        
        # 2. Parar el Nodo Base
        await self._full_node.stop()
        
        logging.info(">>> MINER NODE APAGADO <<<")

    def get_full_node(self) -> FullNode:
        return self._full_node