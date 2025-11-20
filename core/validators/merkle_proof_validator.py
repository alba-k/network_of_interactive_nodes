# network_of_interactive_nodes/core/validators/merkle_proof_validator.py
'''
class MerkleProofValidator:
    Herramienta estática que verifica la inclusión de una transacción 
    en un bloque a partir de un Merkle Proof.
    
    Consume: MerkleHasher (Para realizar el hashing de pares).

    Methods:
        verify_proof(tx_hash: str, merkle_root: str, proof_path: List[str]) -> bool:
            1. Valida que el hash de la TX sea la hoja inicial (leaf).
            2. Recorre el 'proof_path' (lista de hashes hermanos).
            3. En cada paso, hashea la raíz actual con el hash hermano (usando MerkleHasher).
            4. Si el resultado final coincide con el Merkle Root esperado, retorna True.
'''

from typing import List
from core.hashing.merkle_hasher import MerkleHasher 

class MerkleProofValidator:

    @staticmethod
    def verify_proof(tx_hash: str, merkle_root: str, proof_path: List[str]) -> bool:
    
        current_root: str = tx_hash
        
        for sibling_hash in proof_path:
            if current_root < sibling_hash:
                current_root = MerkleHasher.hash_pair(current_root, sibling_hash)
            else:
                current_root = MerkleHasher.hash_pair(sibling_hash, current_root)
                
        return current_root == merkle_root