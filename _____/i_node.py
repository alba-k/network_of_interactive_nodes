# core/i_node.py
from abc import ABC, abstractmethod
from typing import Dict, Optional, List, Any # <--- Importar Dict y Any
from core.models.block import Block # Asumido

class INode(ABC):
    """Contrato base para cualquier tipo de Nodo (Servidor) que participa en la lógica central."""
    
    @abstractmethod
    # CORRECCIÓN: Dict debe ser Dict[str, Any]
    def new_transaction(self, tx_data: Dict[str, Any]) -> bool: 
        pass

    @abstractmethod
    def mine_block(self, miner_address: str) -> Optional[Block]:
        pass
        
    @abstractmethod
    def resolve_conflicts(self) -> bool:
        pass
        
    @abstractmethod
    def get_full_chain(self) -> List[Block]:
        pass