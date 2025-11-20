# core/consensus/consensus_rules.py
'''
Clase ConsensusRules:
    Aplica reglas de consenso simplificadas:
    - Almacena la cadena (lista de bloques).
    - Provee el hash del último bloque.
'''

from typing import List, Optional
from core.models.block import Block

class ConsensusRules:
    
    def __init__(self, genesis_block: Block):
        # 1. Iniciar la cadena con el bloque génesis.
        self.chain: List[Block] = [genesis_block]

    def add_block(self, new_block: Block):
        # 2. Añadir un nuevo bloque a la cadena.
        self.chain.append(new_block)

    def get_last_block(self) -> Optional[Block]:
        # 3. Obtener el último bloque de la cadena.
        if not self.chain:
            return None
        return self.chain[-1]

    def get_last_hash(self) -> Optional[str]:
        # 4. Obtener el hash del último bloque.
        last_block = self.get_last_block()
        if not last_block:
            return None
            
        # 5. Retornar el hash del bloque (no el merkle_root).
        return last_block.hash 

    def get_next_index(self) -> int:
        # 6. Obtener el índice para el próximo bloque.
        last_block = self.get_last_block()
        if not last_block:
            return 0 # Índice del Génesis
        return last_block.index + 1