# main.py

import asyncio
import logging
import base64
from typing import Dict, Any # <-- Añadido para el tipado

# --- INICIO DE LA CORRECCIÓN (Error '3ba047') ---
from Crypto.PublicKey import ECC 
# --- FIN DE LA CORRECCIÓN ---

from core.models.blockchain import Blockchain
from core.mempool.mempool import Mempool
from core.consensus.consensus_manager import ConsensusManager
from _____.gateway_node import GatewayNode
from core.nodes.miner_node import MinerNode
from core.dto.api.data_submission import DataSubmission

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)


# --- "Datos Manuales": Generar Claves ---

GATEWAY_ID = "device_sensor_001"
# --- CORRECCIÓN (Error '3ba047') ---
gateway_key = ECC.generate(curve='P-256')

MINER_ID = "miner_node_555"
# --- CORRECCIÓN (Error '3ba047') ---
miner_key = ECC.generate(curve='P-256')

# (Tipado explícito para ayudar al linter)
PUBLIC_KEY_MAP: Dict[str, Any] = {
    GATEWAY_ID: gateway_key.public_key(),
    MINER_ID: miner_key.public_key()
}


async def main():
    
    logging.info("Creando estado compartido (Blockchain y Mempool)...")
    shared_blockchain = Blockchain()
    shared_mempool = Mempool()
    shared_consensus_manager = ConsensusManager(shared_blockchain)

    logging.info("Inyectando dependencias en los Nodos...")
    
    # (Los errores de '3ba346' (tipo 'Unknown')
    #  se solucionan con la corrección de 'ECC' anterior)
    gateway_node = GatewayNode(
        blockchain=shared_blockchain,
        consensus_manager=shared_consensus_manager,
        public_key_map=PUBLIC_KEY_MAP,
        mempool=shared_mempool,
        private_key=gateway_key, 
        api_host="127.0.0.1",
        api_port=8000,
        host="127.0.0.1",
        port=9001
    )
    
    miner_node = MinerNode(
        blockchain=shared_blockchain,
        consensus_manager=shared_consensus_manager,
        public_key_map=PUBLIC_KEY_MAP,
        mempool=shared_mempool,
        miner_address=MINER_ID,
        host="127.0.0.1",
        port=9002
    )

    try:
        logging.info("Iniciando Nodos (async)...")
        await gateway_node.start()
        await miner_node.start()
        
        await asyncio.sleep(1) 
        logging.info("--- Nodos iniciados y API lista ---")

        # --- 9. SIMULACIÓN ---
        
        logging.info("Simulando llamada API (Dato Manual)...")
        manual_data_str = base64.b64encode(b"25.5 C").decode('utf-8')
        
        manual_submission = DataSubmission(
            source_id=GATEWAY_ID,
            data_type="temperatura",
            value=manual_data_str,
            nonce=1
        )
        
        api_response = await gateway_node.handle_submit_data(manual_submission)
        
        logging.info(f"GatewayNode respondió: {api_response}")
        
        # --- CORRECCIÓN (Errores '3ba386', '3ba782', '3c7d9c') ---
        # (Llamamos al método 'helper', que ahora existe)
        logging.info(f"Mempool ahora tiene {shared_mempool.get_transaction_count()} transacción(es).")
        # --- FIN DE LA CORRECCIÓN ---

        logging.info("MinerNode: Buscando transacciones para minar...")
        new_block = miner_node.create_new_block()
        
        logging.info(f"MinerNode: ¡Bloque {new_block.index} minado!")
        
        logging.info(f"Mempool (pre-validación) tiene {shared_mempool.get_transaction_count()} transacción(es).")

        miner_node.validate_block_rules(new_block)
        
        logging.info(f"Mempool (post-validación) tiene {shared_mempool.get_transaction_count()} transacción(es).")
        
        
        # --- 10. Verificación Final ---
        logging.info("--- VERIFICACIÓN FINAL ---")
        logging.info(f"Altura de la Blockchain: {len(shared_blockchain.chain)}")
        
        data_tx = shared_blockchain.chain[0].data[1]
        data_entry = data_tx.entries[0]
        
        logging.info(f"Dato en Blockchain: {data_entry.source_id}")
        logging.info(f"Valor en Blockchain: {data_entry.value.decode('utf-8')}")

        assert data_entry.source_id == GATEWAY_ID
        assert data_entry.value == b"25.5 C"
        
        logging.info(">>> ¡ÉXITO! El dato manual fue minado en la blockchain.")

    except Exception as e:
        logging.error(f"Error en la simulación: {e}", exc_info=True)
    finally:
        logging.info("Deteniendo Nodos...")
        await gateway_node.stop()
        await miner_node.stop()
        logging.info("--- Simulación terminada ---")


if __name__ == "__main__":
    asyncio.run(main())