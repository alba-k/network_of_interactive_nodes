# network_of_interactive_nodes/core/managers/mining_manager.py
'''
class MiningManager(IMinerRole):
    Implementa el "Software de Minería". 
    
    Es un Gestor (Capa 2) que corre en paralelo al FullNode. 
    No es un nodo por sí mismo; parasita al FullNode para obtener recursos (Mempool, Blockchain)
    y para propagar su trabajo (P2P).

    Attributes:
        _miner_address (str): Dirección (ID) donde se pagará la recompensa (Coinbase).
        _full_node (FullNode): Referencia al nodo anfitrión (para acceder a sus gestores).
        _mining_task (Task): La tarea asíncrona que mantiene el bucle de minería.

    Methods:
        start_mining(): 
            Inicia la tarea de fondo (_mine_loop).
            
        stop_mining(): 
            Cancela la tarea de fondo y espera su cierre.
            
        _mine_loop(interval_seconds): (Bucle Infinito)
            1. Verifica si el Mempool tiene transacciones (usando _full_node.get_mempool()).
            2. Si hay trabajo, llama a create_new_block().
            3. Intenta validar el bloque generado localmente (usando _full_node.get_validation_manager()).
            4. Si es válido, lo propaga a la red (usando _full_node.get_p2p_manager()).

        create_new_block() -> Block: (Implementación de IMinerRole)
            Orquesta la construcción del bloque usando el Núcleo Estático.
            1. Crea la transacción Coinbase.
            2. Selecciona transacciones del Mempool.
            3. Obtiene el último bloque y calcula la dificultad ('bits').
            4. Ejecuta el PoW (BlockBuilder.build).
            
        _create_coinbase_tx() -> Transaction: (Helper)
            Crea la transacción especial que genera nuevas monedas.
            1. Crea un DataEntry con texto arbitrario (nonce/extra-nonce).
            2. Crea la Transacción sin firma (input vacío).
'''

import logging
import asyncio
import time
from typing import Optional

# Interfaces 
from core.interfaces.i_node_roles import IMinerRole

# Modelos y Nodo 
from core.nodes.full_node import FullNode
from core.models.block import Block
from core.models.transaction import Transaction

# Núcleo Estático (Herramientas) 
from core.builders.block_builder import BlockBuilder
from core.factories.transaction_factory import TransactionFactory
from core.factories.data_entry_factory import DataEntryFactory
from core.consensus.difficulty_adjuster import DifficultyAdjuster
from core.utils.difficulty_utils import DifficultyUtils
from core.utils.transaction_utils import TransactionUtils
from core.dto.transaction_creation_params import TransactionCreationParams
from core.dto.data_entry_creation_params import DataEntryCreationParams

class MiningManager(IMinerRole):

    def __init__(self, miner_address: str, full_node: FullNode):
        
        self._miner_address = miner_address
        self._full_node = full_node # Conexión al "Cerebro" del Nodo
        self._mining_task: Optional[asyncio.Task[None]] = None
        
        logging.info("Mining Manager (Software de Minería) preparado.")

    async def start_mining(self):
        if self._mining_task and not self._mining_task.done():
            return
        logging.info("Iniciando servicio de minería...")
        self._mining_task = asyncio.create_task(self._mine_loop())

    async def stop_mining(self):
        if self._mining_task:
            logging.info("Deteniendo servicio de minería...")
            self._mining_task.cancel()
            try:
                await self._mining_task
            except asyncio.CancelledError:
                pass
            self._mining_task = None
            logging.info("Servicio de minería detenido.")

    async def _mine_loop(self, interval_seconds: int = 5):
        logging.info("Bucle de minería activo.")
        
        while True:
            await asyncio.sleep(interval_seconds)
            
            mempool = self._full_node.get_mempool()
            
            if mempool.get_transaction_count() == 0:
                logging.debug("Mineria: Mempool vacío, esperando transacciones...")
                continue

            try:
                logging.info("Mineria: Trabajando en nuevo bloque...")
                
                new_block = self.create_new_block()
                
                validation_manager = self._full_node.get_validation_manager()
                
                if validation_manager.validate_block_rules(new_block):
                    logging.info(f"Mineria: ¡Bloque {new_block.index} MINADO y validado!")
                    
                    p2p_manager = self._full_node.get_p2p_manager()
                    p2p_manager.broadcast_new_block(new_block)
                else:
                    logging.error("Mineria: Bloque generado fue rechazado por reglas internas (¿Cambió la cadena mientras minábamos?).")
                    
            except Exception as e:
                logging.error(f"Mineria: Error crítico en bucle: {e}", exc_info=True)

    # --- Implementación del Rol (Lógica de Creación con Núcleo Estático) ---

    def create_new_block(self) -> Block:
        coinbase_tx = self._create_coinbase_tx()
        
        mempool = self._full_node.get_mempool()
        mempool_txs = mempool.get_transactions_for_block(max_count=10)
        transactions = [coinbase_tx] + mempool_txs
        
        blockchain = self._full_node.get_blockchain()
        last_block = blockchain.last_block
        index = (last_block.index + 1) if last_block else 0
        prev_hash = last_block.hash if last_block else None

        bits = last_block.bits if last_block else DifficultyUtils.target_to_bits(DifficultyUtils.MAX_TARGET)
        
        if DifficultyAdjuster.should_adjust(index) and last_block:
            try:
                prev_adj_index = index - DifficultyAdjuster.ADJUSTMENT_INTERVAL_BLOCKS
                prev_adj_block = blockchain.chain[prev_adj_index]
                bits = DifficultyAdjuster.calculate_new_bits(prev_adj_block, last_block)
            except (IndexError, ValueError):
                pass 

        return BlockBuilder.build(index, transactions, prev_hash, bits)

    def _create_coinbase_tx(self) -> Transaction:
        blockchain = self._full_node.get_blockchain()
        current_height = blockchain.chain[-1].index if blockchain.chain else 0
        
        params_data = DataEntryCreationParams(
            source_id=self._miner_address,
            data_type='coinbase',
            value=f'Mined Block {current_height + 1}'.encode('utf-8'),
            nonce=0
        )
        entry = DataEntryFactory.create(params_data)
        
        tx_size = TransactionUtils.calculate_data_size([entry])
        
        params_tx = TransactionCreationParams(
            entries=[entry],
            timestamp=time.time(),
            fee=0,
            size_bytes=tx_size,
            fee_rate=0.0
        )
        return TransactionFactory.create(params_tx)