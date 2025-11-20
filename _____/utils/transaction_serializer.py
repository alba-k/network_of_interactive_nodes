# transaction_serializer.py
from core.models.transaction import Transaction
from dataclasses import asdict
from typing import Dict, Any

class TransactionSerializer:
    """
    Especialista stateless para convertir un objeto Transaction en dict.
    Usado para transmisión por red (API/Cliente IoT).
    """
    @staticmethod
    def to_dict(transaction: Transaction) -> Dict[str, Any]:
        """Convierte el dataclass a un diccionario."""
        return asdict(transaction)