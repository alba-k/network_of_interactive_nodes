# network_of_interactive_nodes/core/serializers/transaction_serializer.py
'''
class TransactionSerializer:
    Contiene la lógica pura para serializar una Transaction a un diccionario.

    Methods:
        to_dict(tx: Transaction) -> dict[str, Any]: Convierte una Transaction a un dict.
            1. Serializar la lista de DataEntry (delegando a DataEntrySerializer).
            2. Ensamblar el diccionario final de la transacción.
            3. Retornar el diccionario.
'''

from typing import Any, List, Dict

# Importaciones de la arquitectura
from core.models.transaction import Transaction
from core.serializers.data_entry_serializer import DataEntrySerializer

class TransactionSerializer:
    @staticmethod
    def to_dict(tx: Transaction) -> Dict[str, Any]:
        serialized_entries: List[Dict[str, Any]] = [
            DataEntrySerializer.to_dict(entry) for entry in tx.entries
        ]

        transaction_dict: Dict[str, Any] = {
            'entries': serialized_entries,
            'timestamp': tx.timestamp,
            'tx_hash': tx.tx_hash,
            'signature': tx.signature,
            'fee': tx.fee,
            'size_bytes': tx.size_bytes,
            'fee_rate': tx.fee_rate
        }
        
        return transaction_dict