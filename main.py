import asyncio
import logging
import time # Añadir import de time para los nonces de ejemplo
from typing import Dict, List, Tuple, Any, Literal # <--- NECESARIO: Importar Literal

# --- Importaciones de Subsistemas del Core (Mantenidas) ---
from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager

# --- Importaciones de Roles y Fachadas (Los que arrancamos) ---
from core.nodes.full_node import FullNode
from core.nodes.miner_node import MinerNode
from _____.gateway_node import GatewayNode

# --- Subsistema de Identidad ---
from identity.key_persistence import KeyPersistence # Para cargar la clave


# =================================================================
# PASO 1: DEFINICIÓN EXPLÍCITA DE TIPOS PARA EVITAR EL ERROR
# =================================================================

# Definimos el tipo alias para todos los roles permitidos (esto elimina el error del linter)
NodeType = Literal["FULL", "MINER", "GATEWAY"] 

# Usamos el alias para tipar la variable, haciendo que el linter ignore el error
NODE_ROLE: NodeType = "GATEWAY"  # Cambia esto para elegir el rol
HOST: str = "127.0.0.1"
PORT: int = 8888
API_PORT: int = 8000
KEY_FILE: str = 'mi_billetera.pem'


# =================================================================
# PASO 2: LÓGICA PRINCIPAL (Ahora limpia de errores de Literal)
# =================================================================

async def main():
    
    # 1. PREPARACIÓN DEL ESTADO BASE
    # Usamos try/finally para asegurar que los recursos se limpien en caso de error o interrupción
    try:
        my_blockchain = Blockchain()
        my_mempool = Mempool()
        my_consensus = ConsensusManager(blockchain=my_blockchain)
        
        # 2. PREPARACIÓN DE LA IDENTIDAD (Carga o Generación de Clave)
        private_key = KeyPersistence.ensure_key_exists(KEY_FILE)
        
        # Obtenemos la dirección y el mapa de claves necesarias para la inicialización
        miner_address = AddressFactory.generate_p2pkh(private_key.public_key())
        public_key_map = {miner_address: private_key.public_key()}

        
        # 3. CONSTRUCCIÓN DE LA FACHADA (Selección del Rol)
        node_instance: Any # Usamos Any porque el tipo puede ser FullNode, MinerNode, o GatewayNode
        
        if NODE_ROLE == "FULL":
            logging.info("Rol seleccionado: FULL NODE")
            node_instance = FullNode(
                blockchain=my_blockchain,
                consensus_manager=my_consensus,
                public_key_map=public_key_map,
                mempool=my_mempool,
                host=HOST, port=PORT
            )
            
        elif NODE_ROLE == "MINER":
            logging.info("Rol seleccionado: MINER NODE")
            node_instance = MinerNode(
                blockchain=my_blockchain,
                consensus_manager=my_consensus,
                public_key_map=public_key_map, # Necesario para la validación interna
                mempool=my_mempool,
                miner_address=miner_address,
                host=HOST, port=PORT
            )
            
        elif NODE_ROLE == "GATEWAY":
            logging.info("Rol seleccionado: GATEWAY NODE")
            node_instance = GatewayNode(
                blockchain=my_blockchain,
                consensus_manager=my_consensus,
                public_key_map=public_key_map,
                mempool=my_mempool,
                private_key=private_key, # El Gateway necesita la llave para firmar
                host=HOST, port=PORT,
                api_host=HOST, api_port=API_PORT
            )
            
        else:
            logging.critical(f"Rol '{NODE_ROLE}' no válido. Cerrando.")
            return

        # 4. CICLO DE VIDA (Ejecución)
        logging.info(f"Iniciando servicio...")
        await node_instance.start()
        
        # Mantener el programa vivo (asyncio loop)
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logging.info("Interrupción de usuario detectada.")
    except Exception as e:
        logging.critical(f"Error fatal durante la ejecución: {e}", exc_info=True)
    finally:
        if 'node_instance' in locals() and node_instance:
            await node_instance.stop()
        logging.info("Programa finalizado.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass