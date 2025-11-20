# network_of_interactive_nodes/core/factories/merkle_tree_factory.py
'''
class MerkleTreeFactory:
    Ensambla y crea el objeto MerkleTree final.
    
    Methods:
        create(tx_hashes: List[str], log_layers: bool) -> MerkleTree: Crea el objeto MerkleTree final.
            1. Calcular el Merkle Root.
            2. Instanciar el modelo MerkleTree con las hojas y el root.
            3. Retornar la instancia.
'''

from typing import List

# Importaciones de la arquitectura
from core.models.merkle_tree import MerkleTree
from core.services.merkle_root_calculator import MerkleRootCalculator

class MerkleTreeFactory:

    @staticmethod
    def create(tx_hashes: List[str], log_layers: bool = False) -> MerkleTree:

        root_hash: str = MerkleRootCalculator.calculate(
            tx_hashes = tx_hashes, 
            log_layers = log_layers
        )

        new_tree: MerkleTree = MerkleTree(
            leaves = tx_hashes,
            root = root_hash
        )
        
        return new_tree