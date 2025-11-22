# network_of_interactive_nodes/core/managers/mining_manager.py

import logging
import asyncio
import time
from typing import Optional, List, Any # Agregamos Any para flexibilidad
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

    def __init__(self, miner_address: str, full_node: FullNode):
        self._miner_address = miner_address
        self._full_node = full_node
        self._mining_task: Optional[asyncio.Task[None]] = None
        self._executor = ProcessPoolExecutor(max_workers=1)
        logging.info("Mining Manager (Multiprocess) preparado.")

    # --------------------------------------------------------------------------
    # CORRECCIÓN: Ajuste de Tipos para coincidir con IMinerRole y BlockBuilder
    # --------------------------------------------------------------------------
    def create_new_block(self, index: int, transactions: List[Transaction], prev_hash: str, bits: Any) -> Block:
        """
        Implementación de IMinerRole.
        Nota: Usamos 'bits: Any' o 'bits: str' dependiendo de tu BlockBuilder.
        Si BlockBuilder pide str, convertimos aquí.
        """
        # Corrección del error de tipo (Screenshot 1):
        # Convertimos a str explícitamente si BlockBuilder lo requiere estrictamente.
        return BlockBuilder.build(index, transactions, prev_hash, str(bits))

    async def start_mining(self):
        if self._mining_task and not self._mining_task.done():
            return
        logging.info("Iniciando servicio de minería...")
        self._mining_task = asyncio.create_task(self._mine_loop())

    async def stop_mining(self):
        if self._mining_task:
            self._mining_task.cancel()
            try:
                await self._mining_task
            except asyncio.CancelledError:
                pass
            self._mining_task = None
            self._executor.shutdown(wait=False)

    async def _mine_loop(self, interval_seconds: int = 2):
        loop = asyncio.get_running_loop()
        
        while True:
            try:
                await asyncio.sleep(interval_seconds)
                
                # USANDO GETTER (Requiere Paso 1)
                mempool = self._full_node.get_mempool()
                
                if mempool.get_transaction_count() == 0:
                    continue

                logging.info("🔨 MINERIA: Preparando bloque...")
                
                block_params = self._prepare_block_params()
                
                # Ejecución en paralelo
                new_block = await loop.run_in_executor(
                    self._executor, 
                    self.create_new_block, # Llamamos a nuestro método wrapper que corrige los tipos
                    *block_params 
                )
                
                logging.info(f"💎 Bloque {new_block.index} minado.")
                
                # --- CORRECCIÓN DEL ACCESO A FULLNODE (Screenshot 2) ---
                
                # 1. Validación (Usando Getter)
                validation_manager = self._full_node.get_validation_manager()
                
                if validation_manager.validate_block_rules(new_block):
                    
                    # 2. Propagación (Usando Getter y quitando await si no es async)
                    p2p_manager = self._full_node.get_p2p_manager()
                    
                    # Verificamos si es asíncrono o síncrono para evitar error "None is not awaitable"
                    if asyncio.iscoroutinefunction(p2p_manager.broadcast_new_block):
                        await p2p_manager.broadcast_new_block(new_block)
                    else:
                        p2p_manager.broadcast_new_block(new_block)
                    
                    # 3. Consenso (Usando Getter corregido)
                    consensus_manager = self._full_node.get_consensus_manager()
                    
                    # Asumiendo que ValidationManager tiene el mapa de claves público o un getter
                    # Si _public_key_map es protegido, lo ideal es añadir get_public_key_map() en ValidationManager también.
                    # Por ahora accedemos así para desbloquearte:
                    consensus_manager.add_block(new_block, validation_manager._public_key_map)
                    
                else:
                    logging.error("Mineria: Bloque rechazado.")
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logging.error(f"Error mineria: {e}")
                await asyncio.sleep(5)

    def _prepare_block_params(self):
        coinbase_tx = self._create_coinbase_tx()
        mempool = self._full_node.get_mempool()
        transactions = [coinbase_tx] + mempool.get_transactions_for_block(50)
        
        blockchain = self._full_node.get_blockchain()
        last_block = blockchain.last_block
        index = (last_block.index + 1) if last_block else 0
        prev_hash = last_block.hash if last_block else "0"*64 

        # Obtenemos bits como entero
        bits = last_block.bits if last_block else DifficultyUtils.target_to_bits(DifficultyUtils.MAX_TARGET)
        
        if DifficultyAdjuster.should_adjust(index) and last_block:
            try:
                prev_adj = index - Config.DIFFICULTY_ADJUSTMENT_INTERVAL
                if prev_adj >= 0:
                    # Asegúrate de acceder a la lista interna o método getter de blockchain
                    prev_block = blockchain.chain[prev_adj] 
                    bits = DifficultyAdjuster.calculate_new_bits(prev_block, last_block)
            except:
                pass 

        # Retornamos bits. create_new_block se encargará de convertirlo a str si es necesario.
        return (index, transactions, prev_hash, bits)

    def _create_coinbase_tx(self) -> Transaction:
        blockchain = self._full_node.get_blockchain()
        last_block = blockchain.last_block
        idx = last_block.index + 1 if last_block else 0
        
        params_data = DataEntryCreationParams(
            source_id=self._miner_address,
            data_type='coinbase',
            value=f'Block {idx}'.encode(),
            nonce=int(time.time())
        )
        entry = DataEntryFactory.create(params_data)
        tx_size = TransactionUtils.calculate_data_size([entry])
        
        return TransactionFactory.create(TransactionCreationParams(
            entries=[entry], timestamp=time.time(), fee=0, size_bytes=tx_size, fee_rate=0.0
        ))