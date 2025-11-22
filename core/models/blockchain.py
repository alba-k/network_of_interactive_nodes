# network_of_interactive_nodes/core/models/blockchain.py
'''
class Blockchain:
    Contenedor de datos PURO para la cadena de bloques.

    Attributes:
        _chain      (List[Block]):  Lista interna que almacena los objetos Block.

    Methods:
        last_block(property) ->    Optional[Block]:   Retorna el último bloque.
        chain (Property) ->        List[Block]:       Retorna una copia de la cadena.
        add_block_forced(block) -> None:              Añade un bloque (sin validación).
        replace_chain(new_chain) -> None:             Reemplaza toda la cadena.
'''

from typing import List, Optional

# Importaciones de la arquitectura
from core.models.block import Block

class Blockchain:

    def __init__(self):
        self._chain: List[Block] = list()

    @property
    def last_block(self) -> Optional[Block]:
        return self._chain[-1] if self._chain else None
    
    @property
    def chain(self) -> List[Block]:
        return list(self._chain) 
    
    def add_block_forced(self, block: Block) -> None:
        self._chain.append(block)

    def replace_chain(self, new_chain: List[Block]) -> None:
            '''
            Reemplaza la cadena actual por una nueva.
            Usado por el sistema de persistencia al cargar desde disco.
            '''
            self._chain = list(new_chain)