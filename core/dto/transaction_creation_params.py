# network_of_interactive_nodes/core/dto/transaction_creation_params.py
'''
class TransactionCreationParams:
    Agrupa todos los datos *crudos* necesarios por la Factory.

    Attributes:
        entries     (List[DataEntry]):  Lista de DataEntry (inputs y outputs).
        timestamp   (float):            Marca de tiempo UNIX.
        signature   (Optional[str]):    Firma digital (opcional).
        fee         (int):              Comisión total.
        size_bytes  (int):              Tamaño total en bytes.
        fee_rate    (float):            Comisión por byte.
'''

from dataclasses import dataclass
from typing import List, Optional

# Importaciones de la arquitectura
from core.models.data_entry import DataEntry

@dataclass(frozen = True, slots = True)
class TransactionCreationParams:
    entries: List[DataEntry]
    timestamp: float
    signature: Optional[str] = None
    fee: int = 0
    size_bytes: int = 0
    fee_rate: float = 0.0