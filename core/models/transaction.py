# network_of_interactive_nodes/core/models/transaction.py
'''
class Transaction:
    Producto final de la TransactionFactory.

    Attributes:
        entries     (List[DataEntry]):  Lista de DataEntry incluidos en la transacción.
        timestamp   (float):            Marca de tiempo UNIX de creación.
        tx_hash     (str):              Hash calculado sobre los contenidos.
        signature   (Optional[str]):    Firma digital del creador de la transacción.
        fee         (int):              Comisión total de la transacción.
        size_bytes  (int):              Tamaño total de la transacción.
        fee_rate    (float):            Comisión por byte.
'''

from dataclasses import dataclass, field
from typing import List, Optional

# Importaciones de la arquitectura
from core.models.data_entry import DataEntry

@dataclass(frozen=True, slots=True)
class Transaction:
    entries: List[DataEntry]
    timestamp: float
    tx_hash: str
    signature: Optional[str] = field(default = None, compare = False)
    fee: int = field(default = 0, compare=False)
    size_bytes: int = field(default = 0, compare = False)
    fee_rate: float = field(default = 0.0, compare = False)