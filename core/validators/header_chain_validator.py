# network_of_interactive_nodes/core/validators/header_chain_validator.py
'''
class HeaderChainValidator:
    Valida la integridad de una cadena de HEADERS (serializados como dict) recibidos de la red.

    Methods:
        verify(headers, last_known_hash, last_known_timestamp) -> bool: Valida la cadena de headers contra un punto de anclaje conocido.
            1. Validar el Punto de Conexión
            2. Preparar el Bucle de Validación
            3. Validar Campos Malformados (Firma "Paranoica")
            4. Validar Enlace de la Cadena Interna
            5. Validar PoW Firma: Delegación a "Herramienta"
            6. Validar Orden del Timestamp
            7. Actualizar estado para la siguiente iteración
'''

import logging
from typing import List, Dict, Any

# Importaciones de la Arquitectura
from core.utils.difficulty_utils import DifficultyUtils

class HeaderChainValidator:

    @staticmethod
    def verify(headers: List[Dict[str, Any]], 
                 last_known_block_hash: str, 
                 last_known_block_timestamp: int) -> bool:
        
        if not headers:
            return True 

        first_header = headers[0]
        
        if first_header.get('previous_hash') != last_known_block_hash:
            logging.warning('HeaderChainValidator: Cadena huérfana no conecta con el hash conocido.')
            return False

        last_hash: str = last_known_block_hash
        last_timestamp: int = last_known_block_timestamp

        for header_dict in headers:
            
            current_prev_hash = header_dict.get('previous_hash')
            current_hash = header_dict.get('hash')
            current_bits = header_dict.get('bits')
            current_timestamp = header_dict.get('timestamp')

            if (current_prev_hash is None or 
                current_hash is None or 
                current_bits is None or 
                current_timestamp is None):
                
                 logging.warning('HeaderChainValidator: Header malformado (faltan campos clave).')
                 return False

            if current_prev_hash != last_hash:
                logging.warning('HeaderChainValidator: Cadena rota (enlace hash/previous_hash falló).')
                return False

            try:
                target = DifficultyUtils.bits_to_target(current_bits)
                hash_int = int(current_hash, 16)
                
                if hash_int > target:
                     logging.warning(f'HeaderChainValidator: PoW inválido para hash {current_hash[:6]}.')
                     return False
                     
            except (ValueError, TypeError):
                 logging.warning(f'''HeaderChainValidator: Header con 'bits' o 'hash' corrupto.''')
                 return False

            if current_timestamp <= last_timestamp:
                logging.warning(f'HeaderChainValidator: Timestamp inválido (no monotónico).')
                return False
            
            last_hash = current_hash
            last_timestamp = current_timestamp

        logging.info(f'HeaderChainValidator: Verificados {len(headers)} headers exitosamente.')
        return True