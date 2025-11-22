# network_of_interactive_nodes/core/managers/mining_manager.py

import logging
import asyncio
import time
from typing import Optional, List
from concurrent.futures import ProcessPoolExecutor

# Interfaces 
from core.interfaces.i_node_roles import IMinerRole

# Modelos y Nodo 
from core.nodes.full_node import FullNode
from core.models.transaction import Transaction
from core.models.block import Block 

# Núcleo Estático (Herramientas) 
from core.builders.block_builder import BlockBuilder
from core.factories.transaction_factory import TransactionFactory
from core.factories.data_entry_factory import DataEntryFactory
from core.consensus.difficulty_adjuster import DifficultyAdjuster
from core.utils.difficulty_utils import DifficultyUtils
from core.utils.transaction_utils import TransactionUtils
from core.dto.transaction_creation_params import TransactionCreationParams
from core.dto.data_entry_creation_params import DataEntryCreationParams

# Configuración
from config import Config

class MiningManager(IMinerRole):
    """
    Implementa el "Software de Minería".
    Orquesta la creación de bloques (PoW) en un proceso separado para no bloquear el nodo.
    """

    def __init__(self, miner_address: str, full_node: FullNode):
        self._miner_address = miner_address
        self._full_node = full_node
        self._mining_task: Optional[asyncio.Task[None]] = None
        
        # Pool de procesos dedicado a la minería (CPU Bound)
        self._executor = ProcessPoolExecutor(max_workers=1)
        
        logging.info("Mining Manager (Multiprocess) preparado.")

    # --------------------------------------------------------------------------
    # IMPLEMENTACIÓN DE LA INTERFAZ IMinerRole
    # --------------------------------------------------------------------------
    def create_new_block(self, index: int, transactions: List[Transaction], prev_hash: str, bits: int) -> Block:
        """
        Método requerido por IMinerRole.
        
        [CORRECCIÓN DE TIPOS]:
        - Recibe 'bits' como INT (para cumplir la interfaz).
        - Lo convierte a STR al llamar a BlockBuilder.build (para cumplir con el Builder).
        """
        return BlockBuilder.build(index, transactions, prev_hash, str(bits))

    # --------------------------------------------------------------------------
    # GESTIÓN DEL SERVICIO (Start/Stop)
    # --------------------------------------------------------------------------
    async def start_mining(self):
        if self._mining_task and not self._mining_task.done():
            return
        logging.info("Iniciando servicio de minería (Background Process)...")
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
            
            self._executor.shutdown(wait=False)
            logging.info("Servicio de minería detenido.")

    # --------------------------------------------------------------------------
    # BUCLE PRINCIPAL DE MINERÍA
    # --------------------------------------------------------------------------
    async def _mine_loop(self, interval_seconds: int = 2):
        logging.info("Bucle de minería activo.")
        
        loop = asyncio.get_running_loop()
        
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                
                # 1. Obtener Mempool usando Getter
                mempool = self._full_node.get_mempool()
                
                if mempool.get_transaction_count() == 0:
                    continue

                logging.info("🔨 MINERIA: Preparando nuevo bloque...")
                
                # 2. Preparar parámetros (Tipos asegurados: int, List, str, int)
                block_params = self._prepare_block_params()
                
                # 3. Ejecutar PoW en proceso paralelo (Bloqueante para CPU, pero no para Asyncio)
                new_block = await loop.run_in_executor(
                    self._executor, 
                    self.create_new_block, # Llama al método que ajusta los tipos
                    *block_params 
                )
                
                logging.info(f"💎 ¡EUREKA! Bloque {new_block.index} minado. Hash: {new_block.hash[:8]}")
                
                # 4. Validar Bloque (Usando Getter)
                validation_manager = self._full_node.get_validation_manager()
                
                if validation_manager.validate_block_rules(new_block):
                    
                    # 5. Propagar Bloque (Usando Getter)
                    p2p_manager = self._full_node.get_p2p_manager()
                    
                    # [CORRECCIÓN ASYNC]: Verificamos si es corrutina antes de hacer await
                    if asyncio.iscoroutinefunction(p2p_manager.broadcast_new_block):
                        await p2p_manager.broadcast_new_block(new_block)
                    else:
                        p2p_manager.broadcast_new_block(new_block)
                    
                    # 6. Agregar a Consenso Local (Usando Getters para todo)
                    consensus_manager = self._full_node.get_consensus_manager()
                    
                    # [CORRECCIÓN]: Usamos el getter público de ValidationManager
                    pub_key_map = validation_manager.get_public_key_map()
                    
                    consensus_manager.add_block(new_block, pub_key_map)
                    
                else:
                    logging.error("Mineria: Bloque generado fue rechazado (Stale Block o Inválido).")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Mineria: Error crítico en bucle: {e}")
                # Pausa de seguridad
                await asyncio.sleep(5)

    # --------------------------------------------------------------------------
    # MÉTODOS AUXILIARES
    # --------------------------------------------------------------------------
    def _prepare_block_params(self):
        """
        Prepara los datos. Asegura que 'bits' se retorne como INT para evitar errores en run_in_executor.
        """
        coinbase_tx = self._create_coinbase_tx()
        
        mempool = self._full_node.get_mempool()
        mempool_txs = mempool.get_transactions_for_block(max_count=50)
        transactions = [coinbase_tx] + mempool_txs
        
        blockchain = self._full_node.get_blockchain()
        last_block = blockchain.last_block
        
        index = (last_block.index + 1) if last_block else 0
        prev_hash = last_block.hash if last_block else "0"*64 

        # [CORRECCIÓN]: Forzamos conversión a INT aquí
        if last_block:
            bits = int(last_block.bits)
        else:
            bits = int(DifficultyUtils.target_to_bits(DifficultyUtils.MAX_TARGET))
        
        # Ajuste de Dificultad
        if DifficultyAdjuster.should_adjust(index) and last_block:
            try:
                prev_adj_index = index - Config.DIFFICULTY_ADJUSTMENT_INTERVAL
                if prev_adj_index >= 0:
                    prev_adj_block = blockchain.chain[prev_adj_index]
                    # El adjuster devuelve int, pero aseguramos
                    bits = int(DifficultyAdjuster.calculate_new_bits(prev_adj_block, last_block))
            except (IndexError, ValueError):
                pass 

        return (index, transactions, prev_hash, bits)

    def _create_coinbase_tx(self) -> Transaction:
        blockchain = self._full_node.get_blockchain()
        last_block = blockchain.last_block
        current_height = last_block.index if last_block else -1
        
        params_data = DataEntryCreationParams(
            source_id=self._miner_address,
            data_type='coinbase',
            value=f'Mined Block {current_height + 1}'.encode('utf-8'),
            nonce=int(time.time())
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