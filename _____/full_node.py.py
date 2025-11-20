# core/full_node.py
import uuid
import logging
from typing import Set, Optional, Dict, List, Any 
import time

# Imports de Arquitectura y servicios
from core.models.block import Block # Asumido
from core.models.transaction import Transaction # Asumido
from core.models.blockchain import Blockchain # Asumido
from core._____.wallet import Wallet 
from core.mempool.mempool import Mempool 
from core.i_node import INode 

# --- PLACEHOLDERS (ASUMIDOS) ---
class Validator:
    def is_transaction_valid(self, tx: Transaction) -> bool: return True
class IConsensus:
    def create_coinbase_transaction(self, addr: str) -> Transaction: 
        # Aseguramos que el placeholder retorne una TX completa
        return Transaction("COINBASE_SENDER", addr, 10.0, timestamp=time.time(), signature="COINBASE_SIG")
    def proof_of_work(self, last_proof: int) -> int: return 101
# ---------------------------------

class FullNode(INode): 
    
    def __init__(self, consensus: IConsensus):
        self.node_id: str = str(uuid.uuid4()).replace('-', '')
        self.wallet: Wallet = Wallet() 
        self.mempool: Mempool = Mempool()
        self.validator: Validator = Validator()
        self.consensus: IConsensus = consensus
        # Blockchain debe ser inicializada con el consenso
        self.blockchain: Blockchain = Blockchain(self.consensus) 
        self.peer_nodes: Set[str] = set()

    # --- Implementaciones del Contrato INode ---

    def new_transaction(self, tx_data: Dict[str, Any]) -> bool:
        '''Implementación: Recibe JSON, valida y añade a Mempool.'''
        try:
            # Asume que Transaction tiene from_dict()
            transaction = Transaction.from_dict(tx_data) 
            
            if not self.validator.is_transaction_valid(transaction):
                logging.warning("Transacción recibida es inválida.")
                return False

            return self.mempool.add_transaction(transaction)
        except Exception:
            return False

    def mine_block(self, miner_address: str) -> Optional[Block]:
        '''Implementación: Ejecuta el consenso (PoW).'''
        transactions_to_include = self.mempool.get_transactions_for_block()
        coinbase_tx = self.consensus.create_coinbase_transaction(miner_address)
        transactions_to_include.insert(0, coinbase_tx) 

        # Asume que Blockchain.mine_block está definido
        new_block = self.blockchain.mine_block(transactions_to_include) 

        if new_block:
            self.mempool.remove_mined_transactions(transactions_to_include) 
            logging.info(f"Bloque #{new_block.index} minado con éxito.")
            return new_block
        
        return None

    def resolve_conflicts(self) -> bool:
        '''Implementación: Resuelve conflictos de cadena (consenso P2P).'''
        # Lógica de "cadena más larga"
        return True 

    def get_full_chain(self) -> List[Block]:
        '''Implementación: Retorna el estado de la cadena.'''
        return self.blockchain.chain
    
    def register_node(self, address: str) -> bool:
        # Lógica de registro de nodo P2P
        pass