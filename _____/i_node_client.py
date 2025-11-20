# i_node_client.py
from abc import ABC, abstractmethod
from core.models.transaction import Transaction # Asumido
from typing import Protocol, runtime_checkable

# Usamos Protocol para ser más flexibles en la implementación del cliente
@runtime_checkable
class INodeClient(Protocol):
    """Interfaz para clientes ligeros (IoT, Móvil)."""
    
    @abstractmethod
    def get_public_address(self) -> str:
        pass

    @abstractmethod
    def sign_transaction(self, recipient: str, amount: float) -> Transaction:
        pass

    @abstractmethod
    def send_transaction(self, transaction: Transaction) -> bool:
        pass