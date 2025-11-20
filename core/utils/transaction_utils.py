# core/utils/transaction_utils.py
'''
class TransactionUtils:
    Contiene lógica "helper" (de utilidad) pura para manejar transacciones y sus componentes (DataEntry).
    
    Methods:
        calculate_data_size(entries: List[DataEntry]) -> int: Calcula el tamaño (en bytes) del "payload" principal (source_id, data_type, value) de una lista de DataEntry.
'''

from typing import List
from core.models.data_entry import DataEntry

class TransactionUtils:

    @staticmethod
    def calculate_data_size(entries: List[DataEntry]) -> int:
        total_size = 0
        for e in entries:
            total_size += len(e.source_id.encode('utf-8'))
            total_size += len(e.data_type.encode('utf-8'))
            total_size += len(e.value) # (value es bytes)
        return total_size
    
    