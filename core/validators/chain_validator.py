# network_of_interactive_nodes/core/validators/chain_validator.py
'''
class ChainValidator:
    Servicio que valida la integridad de una 'Blockchain' completa.

    Methods:
        verify(blockchain: Blockchain) -> bool:
            1. Obtener la lista de bloques (la 'cadena') del objeto.
            2. Iterar sobre la cadena, bloque por bloque.
            3. Validar el Bloque Génesis (si existe).
            4. Validar bloques subsecuentes (Índice, Hash Previo, PoW).
            5. Si todos los bloques son válidos, retornar True.
'''

import logging
from typing import List

# Importaciones de la arquitectura
from core.models.blockchain import Blockchain
from core.models.block import Block
from core.validators.block_validator import BlockValidator

class ChainValidator:

    @staticmethod
    def verify(blockchain: Blockchain) -> bool:
        
        chain: List[Block] = blockchain.chain
        
        if not chain:
            logging.info('Cadena vacía, validación trivial (True).')
            return True
        
        for i in range(len(chain)):
            current_block = chain[i]

            if i == 0:
                if current_block.index != 0:
                    logging.error('Validación Cadena: Génesis tiene índice != 0.')
                    return False
                if current_block.previous_hash is not None:
                    logging.error('Validación Cadena: Génesis tiene hash previo.')
                    return False
            
            else:
                last_block = chain[i - 1]
                
                if current_block.index != (last_block.index + 1):
                    logging.error(f'Validación Cadena: Índice roto en bloque {current_block.index}.')
                    return False
                
                if current_block.previous_hash != last_block.hash:
                    logging.error(f'Validación Cadena: Hash previo roto en bloque {current_block.index}.')
                    return False
                
            if not BlockValidator.verify(current_block):
                logging.error(f'Validación Cadena: Bloque {current_block.index} falló verificación PoW.')
                return False
            
        logging.info('Validación Cadena: La cadena completa es válida.')
        return True