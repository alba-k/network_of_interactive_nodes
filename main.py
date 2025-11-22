# main.py
'''
Script: main.py
----------------------------------------------------------------------
Propósito: Punto de entrada principal (Entry Point).
           Inicializa el nodo con Persistencia, Configuración y Red.
           
Uso:
    python main.py [ROLE] [MY_PORT] [PEER_IP] [PEER_PORT]
    
    Ejemplos:
    - Minero (PC1): python main.py MINER 9000
    - Gateway (PC2): python main.py GATEWAY 8888 192.168.1.50 9000
'''

import asyncio
import logging
import sys
import os
from typing import Dict, Any, List, Tuple, Literal

# Configuración de Imports para asegurar visibilidad del módulo 'core'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importaciones de Modelos Base
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

# Importaciones de Nodos (Fachadas)
from core.nodes.full_node import FullNode
from core.nodes.miner_node import MinerNode
from core.nodes.gateway_node import GatewayNode

# Importaciones de Identidad
from identity.key_persistence import KeyPersistence
from identity.address_factory import AddressFactory
from Crypto.PublicKey.ECC import EccKey

# Importaciones de Persistencia (Mejora clave)
from core.persistence.strategies.json_strategy import JsonStrategy
from core.managers.persistence_manager import PersistenceManager

# Importación de Configuración Centralizada
from config import Config

NodeType = Literal["FULL", "MINER", "GATEWAY"]

# --- LECTURA DE ARGUMENTOS (CMD) ---
args: List[str] = sys.argv

# 1. Rol (Default FULL)
ROLE: str = args[1].upper() if len(args) > 1 else "FULL"

# 2. Mi Puerto (Default 8888)
MY_PORT: int = int(args[2]) if len(args) > 2 else Config.NETWORK_DEFAULT_PORT

# 3. IP del Vecino (Default None)
PEER_IP: str | None = args[3] if len(args) > 3 else None

# 4. Puerto del Vecino (Default None)
PEER_PORT: int | None = int(args[4]) if len(args) > 4 else None

# --- CONFIGURACIÓN DE RED ---
HOST: str = "0.0.0.0" 

SEED_PEERS: List[Tuple[str, int]] = [(PEER_IP, PEER_PORT)] if (PEER_IP and PEER_PORT) else []

KEY_FILE: str = f"wallet_{MY_PORT}.pem"

logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(levelname)s] %(module)s: %(message)s',
    datefmt='%H:%M:%S'
)

async def main() -> None:
    logging.info(f"=== INICIANDO {ROLE} EN PUERTO {MY_PORT} ===")
    logging.info(f"=== ESCUCHANDO EN: {HOST} (Visible en LAN) ===")
    
    if SEED_PEERS:
        logging.info(f"=== CONECTANDO A: {SEED_PEERS} ===")

    # 1. CONFIGURACIÓN DE PERSISTENCIA
    # Creamos una carpeta por puerto para no mezclar datos si corremos varios nodos locales
    data_dir: str = f"data_node_{MY_PORT}"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
    
    db_path: str = os.path.join(data_dir, "blockchain.json")
    
    # Inyección de Dependencia: Estrategia JSON (Atómica)
    persistence_strategy = JsonStrategy(filepath=db_path)
    persistence_manager = PersistenceManager(strategy=persistence_strategy)

    # 2. PREPARACIÓN DEL ESTADO BASE
    my_blockchain = Blockchain()
    my_mempool = Mempool()
    my_consensus = ConsensusManager(blockchain=my_blockchain)
    public_key_map: Dict[str, EccKey] = {} 

    # Carga de claves conocidas (Web y Sensor) para la demo
    try:
        known_keys: List[str] = ["user_key.pem", "sensor_key.pem", "clients/esp32_sensor/sensor_key.pem"]
        for key_name in known_keys:
            if os.path.exists(key_name):
                k = KeyPersistence.ensure_key_exists(key_name)
                addr = AddressFactory.generate_p2pkh(k.public_key())
                public_key_map[addr] = k.public_key()
                logging.info(f"🔓 ACCESO CONCEDIDO: {key_name}")
    except Exception:
        pass

    # 3. GESTIÓN DE IDENTIDAD DEL NODO
    try:
        private_key = KeyPersistence.ensure_key_exists(KEY_FILE)
        my_public_key = private_key.public_key()
        my_address = AddressFactory.generate_p2pkh(my_public_key)
        logging.info(f"Identidad del Nodo: {my_address}")
    except Exception as e:
        logging.critical(f"Error fatal de identidad: {e}")
        return

    # 4. CONSTRUCCIÓN DE LA FACHADA (NODE)
    node_instance: Any = None

    if ROLE == "FULL":
        node_instance = FullNode(
            blockchain=my_blockchain, consensus_manager=my_consensus,
            public_key_map=public_key_map, mempool=my_mempool,
            host=HOST, port=MY_PORT, seed_peers=SEED_PEERS,
            persistence_manager=persistence_manager
        )

    elif ROLE == "MINER":
        node_instance = MinerNode(
            blockchain=my_blockchain, consensus_manager=my_consensus,
            public_key_map=public_key_map, mempool=my_mempool,
            miner_address=my_address, 
            host=HOST, port=MY_PORT, seed_peers=SEED_PEERS,
            persistence_manager=persistence_manager
        )

    elif ROLE == "GATEWAY":
        API_PORT = 8000 if MY_PORT == 8888 else MY_PORT + 1
        node_instance = GatewayNode(
            blockchain=my_blockchain, consensus_manager=my_consensus,
            public_key_map=public_key_map, mempool=my_mempool,
            private_key=private_key, 
            host=HOST, port=MY_PORT,
            api_host="0.0.0.0", api_port=API_PORT, 
            seed_peers=SEED_PEERS,
            persistence_manager=persistence_manager
        )
    
    else:
        logging.critical(f"Rol desconocido: {ROLE}")
        return

    # 5. EJECUCIÓN
    try:
        # El start del nodo cargará la blockchain del disco si existe (gracias al PersistenceManager)
        await node_instance.start()
        
        # Bucle infinito para mantener el nodo vivo
        while True: 
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("Deteniendo nodo por solicitud de usuario...")
    except asyncio.CancelledError:
        logging.info("Tarea cancelada. Cerrando...")
    finally:
        if node_instance: 
            await node_instance.stop()

if __name__ == "__main__":
    try:
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        pass