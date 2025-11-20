# network_of_interactive_nodes/core/dto/transaction_hashing_data.py
'''
class TransactionHashingData:
    Agrupa los datos que el Hasher necesita para su cálculo.

    Attributes:
        entries     (List[DataEntry]):  Lista de DataEntry a incluir en el hash.
        timestamp   (float):            Marca de tiempo de la transacción.
'''

from dataclasses import dataclass
from typing import List

# Importaciones de la arquitectura
from core.models.data_entry import DataEntry

@dataclass(frozen = True, slots = True)
class TransactionHashingData:
    entries: List[DataEntry]
    timestamp: float