# network_of_interactive_nodes/run_miner.py
'''
Archivo de Arranque (Real) para el MinerNode.

Carga el "Directorio" (Claves Públicas) desde /config_keys/
e inicia el nodo.

Este es el Proceso 2. Se conecta al Gateway (Proceso 1)
usando 'seed_peers'.
'''

import asyncio
import logging
from typing import Dict, Any, List, Tuple

# --- Importaciones de la Arquitectura ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager
from _____.miner_node import MinerNode

# --- Importaciones de "Herramientas" (Día 2) ---
from core.security.ecdsa_public_key_loader import EcdsaPublicKeyLoader

# --- Configuración de Logging ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)

# --- Configuración de Identidades y Red ---
GATEWAY_ID = "device_sensor_001"
MINER_ID = "miner_node_555"
KEY_PATH = "config_keys"
# (La dirección P2P del Gateway que iniciamos primero)
GATEWAY_PEER_ADDRESS: List[Tuple[str, int]] = [("127.0.0.1", 9001)]

async def main():
    logging.info("--- (REAL) Iniciando Miner Node (Proceso 2) ---")

    try:
        # --- 1. Implementación de "Herramientas" (CARGAR claves) ---
        # (El Miner no necesita su clave privada, solo la pública
        #  para el "Directorio" y validar firmas)
        logging.info("Cargando claves públicas (Directorio)...")
        gateway_pub_key = EcdsaPublicKeyLoader.load(
            f"{KEY_PATH}/{GATEWAY_ID}_key.pub"
        )
        miner_pub_key = EcdsaPublicKeyLoader.load(
            f"{KEY_PATH}/{MINER_ID}_key.pub"
        )
        
        # 2. Construir el "Directorio" (Debe ser idéntico al del Gateway)
        PUBLIC_KEY_MAP: Dict[str, Any] = {
            GATEWAY_ID: gateway_pub_key,
            MINER_ID: miner_pub_key
        }
        
    except (IOError, ValueError, FileNotFoundError) as e:
        logging.error(f"FATAL: No se pudieron cargar las claves. {e}")
        logging.error("Asegúrate de ejecutar 'python -m generate_keys' primero.")
        return

    # --- 3. Inyección de Dependencias (DIP) ---
    miner_blockchain = Blockchain()
    miner_mempool = Mempool()
    miner_consensus = ConsensusManager(miner_blockchain)

    # 4. "Ensamblaje Final" del Nodo
    miner_node = MinerNode(
        blockchain=miner_blockchain,
        consensus_manager=miner_consensus,
        public_key_map=PUBLIC_KEY_MAP,
        mempool=miner_mempool,
        miner_address=MINER_ID,       # <-- Su dirección de recompensa
        host="127.0.0.1",
        port=9002,                    # <-- Puerto P2P DIFERENTE
        seed_peers=GATEWAY_PEER_ADDRESS # <-- Se conecta al Gateway
    )
    
    try:
        # (Esto inicia el P2P y el BUCLE DE MINERÍA automático)
        await miner_node.start()
        logging.info("--- Miner Node listo (P2P en 9002) ---")
        # Mantener el proceso vivo para siempre
        await asyncio.Event().wait()
        
    except KeyboardInterrupt:
        logging.info("Deteniendo Miner Node...")
    finally:
        await miner_node.stop()

if __name__ == "__main__":
    asyncio.run(main())