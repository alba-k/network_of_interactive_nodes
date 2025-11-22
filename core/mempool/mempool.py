# network_of_interactive_nodes/core/mempool/mempool.py
'''
class Mempool:
    Gestiona la colección de transacciones pendientes (no minadas).
    Implementa políticas de retención, limpieza y límites de seguridad usando Config.

    *** ACTUALIZACIÓN: Usa core.config.Config y añade protección DoS por tamaño máximo. ***

    Attributes:
        _pending_transactions (Dict[str, Transaction]): Mapa Hash -> TX.
        _arrival_times (Dict[str, float]): Mapa Hash -> Timestamp llegada.
        _lock (threading.Lock): Candado para concurrencia.
'''

from typing import List, Dict, Optional
import time
import threading
import logging

# Importaciones de Modelos
from core.models.transaction import Transaction

# --- IMPORTACIÓN DE CONFIGURACIÓN ---
from config import Config

class Mempool:

    def __init__(self):
        self._pending_transactions: Dict[str, Transaction] = {}
        self._arrival_times: Dict[str, float] = {} 
        self._lock = threading.Lock()
        logging.info(f'Mempool inicializada. Límite: {Config.MEMPOOL_MAX_SIZE} TXs. Expiración: {Config.MEMPOOL_EXPIRY_SEC}s')

    def add_transaction(self, transaction: Transaction) -> bool:
        with self._lock:
            tx_hash: str = transaction.tx_hash

            # 1. Verificar duplicados
            if tx_hash in self._pending_transactions:
                return False

            # -----------------------------------------------------------------
            # [FIX SEGURIDAD] Límite de Memoria (DoS Protection)
            # Si la mempool está llena, rechazamos nuevas transacciones
            # para evitar que el nodo colapse por falta de RAM.
            # -----------------------------------------------------------------
            if len(self._pending_transactions) >= Config.MEMPOOL_MAX_SIZE:
                logging.warning(f"Mempool: Rechazada TX {tx_hash[:6]}. Pool lleno ({Config.MEMPOOL_MAX_SIZE} TXs).")
                return False

            # 2. Almacenar la transacción
            self._pending_transactions[tx_hash] = transaction

            # 3. Registrar el tiempo de llegada
            self._arrival_times[tx_hash] = time.time()

            return True

    def get_transactions_for_block(self, max_count: int = 10) -> List[Transaction]:
        with self._lock:
            # Nota: Sigue pendiente la optimización de ordenamiento (heapq),
            # pero mantenemos la lógica original por estabilidad ahora.
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
                if tx.tx_hash in self._pending_transactions:
                    del self._pending_transactions[tx.tx_hash]

                if tx.tx_hash in self._arrival_times:
                    del self._arrival_times[tx.tx_hash]

    def prune_expired_transactions(self) -> int:
        '''
        Limpia transacciones que han estado esperando más tiempo del permitido en Config.
        '''
        with self._lock:
            now = time.time()
            expired_hashes: List[str] = []

            for tx_hash, arrival_time in self._arrival_times.items():
                age = now - arrival_time
                
                # Usamos la configuración centralizada en lugar del valor hardcodeado
                if age > Config.MEMPOOL_EXPIRY_SEC:
                    expired_hashes.append(tx_hash)

            for tx_hash in expired_hashes:
                if tx_hash in self._pending_transactions:
                    del self._pending_transactions[tx_hash]

                if tx_hash in self._arrival_times:
                    del self._arrival_times[tx_hash]

            if expired_hashes:
                logging.info(f"Mempool: Purga realizada. {len(expired_hashes)} TXs expiradas eliminadas.")

            return len(expired_hashes)

    def have_transaction(self, tx_hash: str) -> bool:
        with self._lock:
            return tx_hash in self._pending_transactions

    def get_transaction(self, tx_hash: str) -> Optional[Transaction]:
        with self._lock:
            return self._pending_transactions.get(tx_hash)

    def get_transaction_count(self) -> int:
        with self._lock:
            return len(self._pending_transactions)