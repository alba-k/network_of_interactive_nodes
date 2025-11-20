# network_of_interactive_nodes/core/nodes/miner_node.py
'''
class MinerNode(FullNode, IMinerRole):
    Implementa un FullNode con la capacidad de minar (IMinerRole).
    
    Attributes:
        _miner_address (str): Dirección (ID) para recibir la recompensa del bloque.
        _mining_task (asyncio.Task[None] | None): La tarea de fondo (async) que ejecuta el bucle de minería.
        (Hereda _blockchain, _consensus_manager, _mempool, _p2p_service de FullNode) 
    
    Methods:
        start(): (Override) Inicia el P2P (padre) y lanza el bucle de minería.
            1. Llama a FullNode.start()
            2. Lanza self._mine_loop() como una tarea (asyncio.create_task).
            
        stop(): (Override) Detiene el bucle de minería y el P2P (padre).
            1. Cancela la self._mining_task.
            2. Llama a FullNode.stop().
            
        _mine_loop(): (Helper Async) Bucle de minería activo.
            1. Espera X segundos.
            2. Comprueba el Mempool (get_transaction_count).
            3. Si hay TXs, llama a self.create_new_block().
            4. Llama a self.validate_block_rules() para propagar el bloque.
            5. Repite.

        create_new_block(): (IMinerRole) Orquesta la creación de un nuevo bloque.
            1. Crear la transacción Coinbase (Delega a _create_coinbase_tx).
            2. Obtener transacciones del Mempool (Accede a _mempool).
            3. Calcular 'bits' de dificultad (Delega a DifficultyAdjuster).
            4. Construir y minar el bloque (Delega a BlockBuilder).
            5. Retornar el bloque minado.

        _create_coinbase_tx(): (Helper) Crea la transacción de recompensa.
            1. Crear DTO para DataEntry (DataEntryCreationParams).
            2. Delegar creación del DataEntry (DataEntryFactory).
            3. Crear DTO para Transacción (TransactionCreationParams).
            4. Delegar creación de la TX (TransactionFactory).
            5. Retornar la TX coinbase.
'''

import logging
import time 
import asyncio # <-- IMPORTANTE para el bucle
from typing import Dict, List, Tuple, Optional
from Crypto.PublicKey.ECC import EccKey

# ... (El resto de tus importaciones) ...
from core.nodes.full_node import FullNode
from core.interfaces.i_node_roles import IMinerRole
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.models.transaction import Transaction 
from core.consensus.consensus_manager import ConsensusManager
from core.mempool.mempool import Mempool 
from core.utils.transaction_utils import TransactionUtils
from core.builders.block_builder import BlockBuilder
from core.factories.transaction_factory import TransactionFactory
from core.factories.data_entry_factory import DataEntryFactory 
from core.consensus.difficulty_adjuster import DifficultyAdjuster 
from core.utils.difficulty_utils import DifficultyUtils 
from core.dto.transaction_creation_params import TransactionCreationParams
from core.dto.data_entry_creation_params import DataEntryCreationParams 

class MinerNode(FullNode, IMinerRole):

    def __init__(self, 
                 blockchain: Blockchain, 
                 consensus_manager: ConsensusManager, 
                 public_key_map: Dict[str, EccKey], 
                 mempool: Mempool, 
                 miner_address: str, 
                 host: str, 
                 port: int,
                 seed_peers: Optional[List[Tuple[str, int]]] = None):
        
        FullNode.__init__(self, 
            blockchain, 
            consensus_manager, 
            public_key_map, 
            mempool, 
            host, 
            port, 
            seed_peers
        )
        
        self._miner_address = miner_address
        
        # --- TRAMO 1: CORRECCIÓN (Error '3e569c') ---
        # (El linter necesita saber el tipo de retorno de la Tarea)
        self._mining_task: asyncio.Task[None] | None = None
        # --- FIN DE LA CORRECCIÓN ---
        
        logging.info('Miner Node (FullNode + Minería) inicializado.')
        
    async def _mine_loop(self, interval_seconds: int = 10):
        logging.info(f"Bucle de minería iniciado. Buscando trabajo cada {interval_seconds}s...")
        
        while True:
            await asyncio.sleep(interval_seconds)
            
            # --- TRAMO 2: CORRECCIÓN (Error '3e569c') ---
            # (Esta llamada es correcta, pero el método
            #  debe existir en mempool.py - ver Corrección 2)
            if self._mempool.get_transaction_count() == 0:
            # --- FIN DE LA CORRECCIÓN ---
                logging.debug("MinerLoop: Mempool vacío, esperando...")
                continue 
                
            logging.info(f"MinerLoop: ¡Mempool tiene {self._mempool.get_transaction_count()} TXs! Iniciando minería...")
            
            try:
                new_block = self.create_new_block()
                self.validate_block_rules(new_block)
                logging.info(f"MinerLoop: ¡Bloque {new_block.index} minado y propagado!")
                
            except Exception as e:
                logging.error(f"MinerLoop: Error durante la minería: {e}", exc_info=True)


    async def start(self): 
        await FullNode.start(self) 
        logging.info('Miner Node iniciando bucle de minería...')
        self._mining_task = asyncio.create_task(self._mine_loop())

    async def stop(self) -> None:
        if self._mining_task:
            logging.info("Deteniendo bucle de minería...")
            self._mining_task.cancel()
            try:
                await self._mining_task
            except asyncio.CancelledError:
                logging.info("Bucle de minería detenido.")
        
        await FullNode.stop(self)

    # ... (El resto de tu código: create_new_block y _create_coinbase_tx
    #      permanecen sin cambios, ya son correctos) ...

    def create_new_block(self) -> Block:
        logging.info('Miner Node: Creando nuevo bloque...')
        
        coinbase_tx: Transaction = self._create_coinbase_tx()
        
        mempool_txs: List[Transaction] = self._mempool.get_transactions_for_block(max_count=10)
        transactions_for_block: List[Transaction] = [coinbase_tx] + mempool_txs
        
        last_block = self._blockchain.last_block
        index = (last_block.index + 1) if last_block else 0
        prev_hash = last_block.hash if last_block else None

        bits: str
        if last_block is None:
            bits = DifficultyUtils.target_to_bits(DifficultyUtils.MAX_TARGET)
        elif DifficultyAdjuster.should_adjust(index):
            try:
                prev_adj_block_index = index - DifficultyAdjuster.ADJUSTMENT_INTERVAL_BLOCKS
                prev_adj_block = self._blockchain.chain[prev_adj_block_index]
                bits = DifficultyAdjuster.calculate_new_bits(prev_adj_block, last_block)
            except (IndexError, ValueError):
                logging.warning(f"MinerNode: Error al ajustar dificultad. Usando bits del bloque anterior.")
                bits = last_block.bits
        else:
            bits = last_block.bits
        
        mined_block = BlockBuilder.build(
            index = index,
            transactions = transactions_for_block,
            previous_hash = prev_hash,
            bits = bits
        )
        
        logging.info(f'Miner Node: ¡Bloque {index} minado! Hash: {mined_block.hash[:6]}...')
        return mined_block

    def _create_coinbase_tx(self) -> Transaction:
        
        current_height = self._get_current_height()
        current_time = time.time()

        coinbase_data_params = DataEntryCreationParams(
            source_id = self._miner_address,
            data_type = 'coinbase_reward',
            value = f'Recompensa Bloque {current_height + 1}'.encode('utf-8'),
            nonce=0,
            metadata={}
        )
        
        coinbase_data_entry = DataEntryFactory.create(coinbase_data_params)
        tx_size = TransactionUtils.calculate_data_size([coinbase_data_entry])

        coinbase_tx_params = TransactionCreationParams(
            entries=[coinbase_data_entry],
            timestamp=current_time,
            signature=None,
            fee=0,
            size_bytes=tx_size,
            fee_rate=0.0
        )
        
        coinbase_tx = TransactionFactory.create(coinbase_tx_params)
        return coinbase_tx