# network_of_interactive_nodes/core/mempool/mempool.py
'''
class Mempool:
    Gestiona la colección de transacciones pendientes (no minadas).

    Attributes:
        _pending_transactions (Dict[str, Transaction]): 
            Un diccionario (mapa) que almacena las transacciones pendientes.
            
        _lock (threading.Lock): 
            Un candado (lock) que previene problemas de concurrencia.

    Methods:
        __init__(): 
            Inicializa el Mempool (crea el dict y el lock).
            
        add_transaction(transaction) -> bool: Añade una transacción al mempool de forma segura.
            1. Adquirir el lock.
            2. Obtener el hash de la TX.
            3. Verificar si el hash ya existe en el dict.
            4. Si existe, retornar False (no se añadió).
            5. Si no existe, añadir la TX al dict.
            6. Liberar el lock (automático con 'with').
            7. Retornar True (se añadió).
            
        get_transactions_for_block(max_count) -> List[Transaction]: Obtiene la lista de transacciones con mayor prioridad.
            1. Adquirir el lock.
            2. Obtener todos los valores (TXs) del dict y convertirlos a lista.
            3. Ordenar la lista de TXs por 'fee_rate' (de mayor a menor).
            4. Retornar la sub-lista (desde el inicio hasta 'max_count').
            5. Liberar el lock.

        remove_mined_transactions(mined_transactions): Limpia el mempool eliminando transacciones que ya fueron minadas.
            1. Adquirir el lock.
            2. Iterar sobre la lista de TXs minadas.
            3. Usar 'pop(tx.tx_hash, None)' para eliminar cada TX del dict.
            4. Liberar el lock.
            
        have_transaction(tx_hash) -> bool: (Helper P2P) Revisa (con lock) si un hash ya existe.
            
        get_transaction(tx_hash) -> Optional[Transaction]: (Helper P2P) Obtiene (con lock) una TX por su hash.
            
        get_transaction_count() -> int: (Helper) Retorna el número de TXs pendientes (de forma segura).
'''

from typing import List, Dict, Optional
from core.models.transaction import Transaction
import threading
import logging

class Mempool:
    
    def __init__(self):
        self._pending_transactions: Dict[str, Transaction] = {}
        self._lock = threading.Lock()
        logging.info('Mempool inicializada.')

    def add_transaction(self, transaction: Transaction) -> bool:
        with self._lock:
            tx_hash: str = transaction.tx_hash
            if tx_hash in self._pending_transactions:
                return False
            self._pending_transactions[tx_hash] = transaction
            return True

    def get_transactions_for_block(self, max_count: int = 10) -> List[Transaction]:
        with self._lock:
            all_txs: List[Transaction] = list(self._pending_transactions.values())
            
            sorted_txs: List[Transaction] = sorted(
                all_txs, 
                key = lambda tx: tx.fee_rate, 
                reverse = True
            )
            return sorted_txs[:max_count]

    def remove_mined_transactions(self, mined_transactions: List[Transaction]):
        with self._lock:
            for tx in mined_transactions:
                self._pending_transactions.pop(tx.tx_hash, None)

    def have_transaction(self, tx_hash: str) -> bool:
        with self._lock:
            return tx_hash in self._pending_transactions

    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        with self._lock:
            return self._pending_transactions.get(tx_hash)

    def get_transaction_count(self) -> int:
        with self._lock:
            return len(self._pending_transactions)