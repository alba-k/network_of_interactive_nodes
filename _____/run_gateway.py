# network_of_interactive_nodes/run_gateway.py
'''
Archivo de Arranque (Real) para el GatewayNode.

Carga las claves permanentes desde /config_keys/ usando las
"Herramientas" (Loaders) e inicia el nodo.   

Este es el Proceso 1 (El "Seed Node").
'''

import asyncio
import logging
from typing import Dict, Any

# --- Importaciones de la Arquitectura ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager
from _____.gateway_node import GatewayNode

# --- Importaciones de "Herramientas" (Día 2) ---
from core.security.ecdsa_private_key_loader import EcdsaPrivateKeyLoader
from core.security.ecdsa_public_key_loader import EcdsaPublicKeyLoader

# --- Configuración de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logging.getLogger("uvicorn").setLevel(logging.WARNING)

# --- Configuración de Identidades y Red ---
GATEWAY_ID = "device_sensor_001"
MINER_ID = "miner_node_555"
KEY_PATH = "config_keys"

async def main():
    logging.info("--- (REAL) Iniciando Gateway Node (Proceso 1) ---")
    
    try:
        # --- 1. Implementación de "Herramientas" (CARGAR claves) ---
        logging.info(f"Cargando clave privada para {GATEWAY_ID}...")
        gateway_priv_key = EcdsaPrivateKeyLoader.load(
            f"{KEY_PATH}/{GATEWAY_ID}_key.pem"
        )
        
        logging.info("Cargando claves públicas (Directorio)...")
        gateway_pub_key = EcdsaPublicKeyLoader.load(
            f"{KEY_PATH}/{GATEWAY_ID}_key.pub"
        )
        miner_pub_key = EcdsaPublicKeyLoader.load(
            f"{KEY_PATH}/{MINER_ID}_key.pub"
        )
        
        # 2. Construir el "Directorio" (PUBLIC_KEY_MAP)
        PUBLIC_KEY_MAP: Dict[str, Any] = {
            GATEWAY_ID: gateway_pub_key,
            MINER_ID: miner_pub_key
        }
        
    except (IOError, ValueError, FileNotFoundError) as e:
        logging.error(f"FATAL: No se pudieron cargar las claves. {e}")
        logging.error("Asegúrate de ejecutar 'python -m generate_keys' primero.")
        return

    # --- 3. Inyección de Dependencias (DIP) ---
    # (Cada nodo "real" tiene su propia memoria)
    gateway_blockchain = Blockchain()
    gateway_mempool = Mempool()
    gateway_consensus = ConsensusManager(gateway_blockchain)

    # 4. "Ensamblaje Final" del Nodo
    gateway_node = GatewayNode(
        blockchain=gateway_blockchain,
        consensus_manager=gateway_consensus,
        public_key_map=PUBLIC_KEY_MAP,
        mempool=gateway_mempool,
        private_key=gateway_priv_key, # <-- Clave Cargada
        api_host="127.0.0.1",
        api_port=8000,
        host="127.0.0.1",
        port=9001,
        seed_peers=None # <-- Es el primer nodo (semilla)
    )
    
    try:
        await gateway_node.start()
        logging.info("--- Gateway Node listo (API en 8000, P2P en 9001) ---")
        # Mantener el proceso vivo para siempre
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logging.info("Deteniendo Gateway Node...")
    finally:
        await gateway_node.stop()

if __name__ == "__main__":
    asyncio.run(main())