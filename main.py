# main.py (CORREGIDO - SIN ERRORES DE TIPADO)
'''
Script: main.py
----------------------------------------------------------------------
Propósito: Punto de entrada principal (Entry Point) UNIFICADO.
           Soporta: FULL, MINER, GATEWAY, SPV y WALLET.
'''

import asyncio
import logging
import sys
import os
import glob
from typing import Dict, Any, List, Tuple, Optional

# Configuración de Imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones Base
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

# Nodos
from core.nodes.full_node import FullNode
from core.nodes.miner_node import MinerNode
from core.nodes.gateway_node import GatewayNode
from core.nodes.spv_node import SPVNode       
from core.nodes.wallet_node import WalletNode 

# Identidad y Persistencia
from identity.key_persistence import KeyPersistence
from identity.address_factory import AddressFactory
from Crypto.PublicKey.ECC import EccKey
from core.persistence.strategies.json_strategy import JsonStrategy
from core.managers.persistence_manager import PersistenceManager
from config import Config

# --- LECTURA DE ARGUMENTOS ---
args = sys.argv
ROLE = args[1].upper() if len(args) > 1 else "FULL"
MY_PORT = int(args[2]) if len(args) > 2 else Config.NETWORK_DEFAULT_PORT
PEER_IP = args[3] if len(args) > 3 else None
PEER_PORT = int(args[4]) if len(args) > 4 else None

# Configuración Red
HOST = "0.0.0.0" 
SEED_PEERS: List[Tuple[str, int]] = [(PEER_IP, PEER_PORT)] if (PEER_IP and PEER_PORT) else []
KEY_FILE = f"wallet_{MY_PORT}.pem"

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(module)s: %(message)s', datefmt='%H:%M:%S')

async def main() -> None:
    logging.info(f"=== INICIANDO {ROLE} EN PUERTO {MY_PORT} ===")
    
    # 1. PERSISTENCIA (Variable unificada para evitar error 'unbound')
    persistence_manager: Optional[PersistenceManager] = None
    
    if ROLE in ["FULL", "MINER", "GATEWAY", "WALLET"]:
        data_dir = f"data_node_{MY_PORT}"
        if not os.path.exists(data_dir): os.makedirs(data_dir, exist_ok=True)
        db_path: str = os.path.join(data_dir, "blockchain.json")
        persistence_strategy = JsonStrategy(filepath=db_path)
        persistence_manager = PersistenceManager(strategy=persistence_strategy)

    # 2. ESTADO BASE
    blockchain = Blockchain()
    mempool = Mempool()
    consensus = ConsensusManager(blockchain=blockchain)
    
    # Carga dinámica de llaves
    public_key_map: Dict[str, EccKey] = {} 
    try:
        pem_files = glob.glob("*.pem")
        for key_path in pem_files:
            try:
                k = KeyPersistence.ensure_key_exists(key_path)
                addr = AddressFactory.generate_p2pkh(k.public_key())
                public_key_map[addr] = k.public_key()
            except Exception: pass
    except Exception as e:
        logging.warning(f"Error cargando llaves: {e}")

    # 3. IDENTIDAD PROPIA
    private_key: Optional[EccKey] = None
    my_address: str = "Observer"
    
    if ROLE != "FULL": 
        try:
            private_key = KeyPersistence.ensure_key_exists(KEY_FILE)
            my_public_key = private_key.public_key()
            my_address = AddressFactory.generate_p2pkh(my_public_key)
            public_key_map[my_address] = my_public_key # Auto-registro
            logging.info(f"Identidad PROPIA: {my_address}")
        except Exception as e:
            logging.warning(f"Iniciando sin identidad firmada (Error: {e})")

    # 4. FACTORY DE NODOS (Usando argumentos con nombre para evitar errores)
    node_instance: Any = None

    if ROLE == "MINER":
        node_instance = MinerNode(
            miner_address=my_address, # [CORRECCIÓN] Este argumento va primero o nombrado
            blockchain=blockchain, 
            consensus_manager=consensus, 
            public_key_map=public_key_map, 
            mempool=mempool, 
            host=HOST, 
            port=MY_PORT, 
            seed_peers=SEED_PEERS, 
            persistence_manager=persistence_manager # [CORRECCIÓN] Usamos la variable correcta
        )
    
    elif ROLE == "GATEWAY":
        if private_key is None:
            logging.critical("Gateway requiere clave privada.")
            return
            
        API_PORT = 8000 + int(str(MY_PORT)[-1]) 
        node_instance = GatewayNode(
            blockchain=blockchain, 
            consensus_manager=consensus, 
            public_key_map=public_key_map, 
            mempool=mempool, 
            private_key=private_key, # Es seguro porque validamos arriba
            host=HOST, 
            port=MY_PORT, 
            api_host="0.0.0.0", 
            api_port=API_PORT, 
            seed_peers=SEED_PEERS, 
            persistence_manager=persistence_manager
        )
    
    elif ROLE == "FULL":
        node_instance = FullNode(
            blockchain=blockchain, 
            consensus_manager=consensus, 
            public_key_map=public_key_map, 
            mempool=mempool, 
            host=HOST, 
            port=MY_PORT, 
            seed_peers=SEED_PEERS, 
            persistence_manager=persistence_manager
        )
        
    elif ROLE == "SPV":
        node_instance = SPVNode(
            host=HOST, 
            port=MY_PORT, 
            seed_peers=SEED_PEERS, 
            wallet_file=KEY_FILE
        )
        
    elif ROLE == "WALLET":
        node_instance = WalletNode(
            blockchain=blockchain, 
            consensus_manager=consensus, 
            public_key_map=public_key_map, 
            mempool=mempool, 
            host=HOST, 
            port=MY_PORT, 
            seed_peers=SEED_PEERS, 
            wallet_file=KEY_FILE, 
            persistence_manager=persistence_manager
        )

    else:
        logging.critical(f"Rol desconocido: {ROLE}")
        return

    # 5. ARRANCAR
    try:
        await node_instance.start()
        while True: await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        await node_instance.stop()

if __name__ == "__main__":
    if sys.platform == 'win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())