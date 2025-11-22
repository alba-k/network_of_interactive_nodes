# network_of_interactive_nodes/core/nodes/gateway_node.py
'''
class GatewayNode:
    Fachada (Facade) que representa el rol de API Gateway y Wallet en la red.
    
    Responsabilidad: COMPOSICIÓN. Ensambla y controla el ciclo de vida de los gestores.
    
    Arquitectura Interna (Cableado):
        1. Crea el FullNode (Base P2P/Validación/Mempool).
        2. Crea el SoftwareSigner (Adaptador de Seguridad con la clave privada).
        3. Crea el WalletManager (Inyectándole el Signer).
        4. Crea el APIManager (Inyectándole el WalletManager y el FullNode).

    Attributes:
        _full_node (FullNode): Nodo base.
        _signer (SoftwareSigner): Adaptador de firma local.
        _wallet_manager (WalletManager): Gestor de identidad.
        _api_manager (APIManager): Servidor Web (FastAPI/Flask).
'''

import logging
from typing import Dict, List, Tuple, Optional
from Crypto.PublicKey.ECC import EccKey

# --- Importaciones de Componentes y Gestores ---
from core.nodes.full_node import FullNode
from core.managers.wallet_manager import WalletManager
from core.managers.api_manager import APIManager
from core.client_services.software_signer import SoftwareSigner 

# --- Importaciones de Modelos Base ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

# --- Importación de Persistencia (Tipado Estricto) ---
from core.managers.persistence_manager import PersistenceManager

class GatewayNode:

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool,
                 private_key: EccKey, 
                 host: str, 
                 port: int,
                 api_host: str = "0.0.0.0", 
                 api_port: int = 8000,
                 seed_peers: Optional[List[Tuple[str, int]]] = None,
                 # [FIX] Tipado estricto
                 persistence_manager: Optional[PersistenceManager] = None):
        
        logging.info("Inicializando Gateway Node...")

        # 1. Instanciar el FullNode (El Motor P2P y de Validación)
        # Le pasamos el persistence_manager para que cargue la cadena al iniciar.
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

        # 2. Preparar la Identidad (Adaptador + Gestor)
        #    a. Creamos el adaptador de firma (SoftwareSigner) con la clave privada.
        self._signer = SoftwareSigner(private_key)
        
        #    b. Instanciamos el WalletManager inyectándole el signer (Cumple DIP).
        self._wallet_manager = WalletManager(
            public_key=private_key.public_key(),
            signer=self._signer
        )

        # 3. Instanciar el API Manager (El Servidor Web)
        #    Le inyectamos el WalletManager (ya configurado) y el FullNode.
        self._api_manager = APIManager(
            wallet_manager=self._wallet_manager,
            full_node=self._full_node,
            api_host=api_host,
            api_port=api_port
        )
        
        logging.info(f"Gateway Node ensamblado. API escuchando en {api_host}:{api_port}")

    async def start(self) -> None:
        logging.info(">>> ARRANCANDO GATEWAY NODE <<<")
        
        # 1. Arrancar el FullNode (Inicia Red P2P y carga Persistencia)
        await self._full_node.start()
        
        # 2. Arrancar el Servidor API (Asíncrono/Threaded según implementación interna)
        self._api_manager.start_api_server()
        
        logging.info(">>> GATEWAY NODE OPERATIVO <<<")

    async def stop(self) -> None:
        logging.info(">>> DETENIENDO GATEWAY NODE <<<")
        
        # 1. Detener Servidor API primero (dejar de recibir peticiones nuevas)
        self._api_manager.stop_api_server()
        
        # 2. Detener el FullNode (Cerrar conexiones P2P y guardar DB)
        await self._full_node.stop()
        
        logging.info(">>> GATEWAY NODE APAGADO <<<")
    
    # --- Getters para acceso a servicios ---
    
    def get_full_node(self) -> FullNode:
        return self._full_node
    
    def get_api_manager(self) -> APIManager:
        return self._api_manager
    
    def get_wallet_manager(self) -> WalletManager:
        return self._wallet_manager