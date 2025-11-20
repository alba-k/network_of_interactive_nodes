# proof_of_stake.py
# Code informal
'''
import logging
from core.consensus.i_consensus import IConsensus
from core.models.block import Block                 # El bloque INMUTABLE
from core.utils.crypto_utils import CryptoUtils    # La calculadora de hash
from typing import Any, Dict, List

# --- SIMULACIÓN DE STAKES (BILLETERAS) ---
DEFAULT_STAKERS = {
    "validator-address-01-alice": 100,
    "validator-address-02-bob": 50,
    "validator-address-03-carol": 250,
    "validator-address-04-dave": 10
}
# --- ---

class ProofOfStake(IConsensus):
    'Implementación de consenso Proof-of-Stake (Prueba de Participación).'

    def __init__(self, my_address: str, initial_stakes: Dict[str, int] = DEFAULT_STAKERS):
        # ... (logging, etc.)
        self._my_address = my_address
        self._stakes: Dict[str, int] = {}
        self._staker_addresses: List[str] = [] # La lista ORDENADA
        self._total_stake: int = 0
        
        self.update_stakes(initial_stakes) 

        if self._my_address not in self._stakes:
            # ... (logging warning)
            self._my_index = -1
        else:
            self._my_index = self._staker_addresses.index(self._my_address)
            # ... (logging info)

    def _select_validator(self, last_block_hash: str) -> str:
        '''
'Elige un validador de forma determinista y ponderada.'
'''
        hash_int = int(last_block_hash, 16)
        
        if self._total_stake == 0:
             return self._staker_addresses[0] if self._staker_addresses else "" 
             
        winning_number = hash_int % self._total_stake
        current_weight = 0
        
        # --- ¡LA CORRECCIÓN CRÍTICA! ---
        # Iteramos sobre la lista ORDENADA ('_staker_addresses')
        # para que la selección sea 100% determinista.
        for address in self._staker_addresses:
            stake_amount = self._stakes[address]
            current_weight += stake_amount
            if winning_number < current_weight:
                return address # ¡Este es el ganador!
                
        return self._staker_addresses[0] # Fallback

    # --- Implementación de Métodos de IConsensus ---

    # --- TU NOMBRE DE VARIABLE (¡ES CORRECTO!) ---
    def execute(self, candidate_block_data: Block) -> Block: 
        '''
'"Forja" un bloque. Verifica si es nuestro turno y sella el bloque.'
'''
        
        if not candidate_block_data.previous_hash:
             logging.info("PoS: 'Forjando' Bloque Génesis (sin elección).")
             return candidate_block_data # Devuelve el candidato génesis

        # 1. Determinar quién DEBE forjar este bloque
        winner_address = self._select_validator(candidate_block_data.previous_hash)
        
        # 2. Comprobar si somos nosotros
        if winner_address != self._my_address:
            logging.debug(f"PoS: No es nuestro turno. El forjador es '{winner_address}'.")
            raise PermissionError("No es el turno de este validador para forjar.")
        
        # 3. ¡ES NUESTRO TURNO!
        logging.info(f"PoS: ¡Es nuestro turno! Forjando bloque #{candidate_block_data.index}...")
        
        final_nonce = self._my_index
        
        # 5. Recalcular el hash final con el nonce correcto
        final_hash = CryptoUtils.calculate_hash(
            index=candidate_block_data.index,
            timestamp=candidate_block_data.timestamp,
            previous_hash=candidate_block_data.previous_hash,
            merkle_root=candidate_block_data.merkle_root,
            difficulty=candidate_block_data.difficulty,
            nonce=final_nonce
        )
        
        # 6. Crear el bloque final e INMUTABLE
        final_block = Block(
            index=candidate_block_data.index,
            timestamp=candidate_block_data.timestamp,
            previous_hash=candidate_block_data.previous_hash,
            difficulty=candidate_block_data.difficulty,
            merkle_root=candidate_block_data.merkle_root,
            data=candidate_block_data.data,
            nonce=final_nonce,           # <-- El nonce (índice del validador)
            hash=final_hash              # <-- El hash final
        )
        
        return final_block

    def validate(self, block: Block) -> bool:
        'Valida si un bloque fue forjado por el validador correcto.'
        
        if block.index == 0:
            return True # Génesis siempre es válido

        if not block.previous_hash:
            logging.error("PoS Validation FAILED: Bloque no-Génesis no tiene hash anterior.")
            return False

        try:
            expected_winner_address = self._select_validator(block.previous_hash)
            expected_winner_index = self._staker_addresses.index(expected_winner_address)
        except Exception as e:
            logging.error(f"PoS Validation FAILED: No se pudo determinar el validador esperado. {e}")
            return False
        
        actual_validator_index = block.nonce
        
        if expected_winner_index == actual_validator_index:
            return True # ¡Válido!
        else:
            logging.warning(f"PoS Validation FAILED: Bloque #{block.index} forjado por validador incorrecto. ...")
            return False
    
    def adjust_parameters(self, **kwargs: Any) -> None:
        'En PoS, esto se usa para actualizar la lista de "stakes".'
        
        # 'new_stakes_raw' es Dict[Any, Any] (Potencialmente inseguro)
        new_stakes_raw = kwargs.get("new_stakes")

        # 1. Validar que es un diccionario
        if not isinstance(new_stakes_raw, dict):
            logging.warning("adjust_parameters: 'new_stakes' no es un diccionario. Ignorando.")
            return

        # --- AQUÍ ESTÁ LA SOLUCIÓN A TU IMAGEN ---
        
        # 2. Validar el contenido (que sea Dict[str, int])
        validated_stakes: Dict[str, int] = {}
        is_valid = True
        
        # Iteramos sobre los datos "desconocidos"
        for key, value in new_stakes_raw.items():
            
            # ¡Esta es la SOLUCIÓN!
            # Verificamos explícitamente el tipo de 'key' y 'value'
            if not isinstance(key, str) or not isinstance(value, int):
                is_valid = False
                logging.error(f"adjust_parameters: Dato de stake inválido: ({key}, {value}). Se esperan (str, int).")
                break # Detener la validación al primer error
            
            if value <= 0: # El stake no puede ser 0 o negativo
                is_valid = False
                logging.error(f"adjust_parameters: El stake para '{key}' debe ser positivo.")
                break
                
            validated_stakes[key] = value # Solo añadimos los datos válidos

        # 3. Si todo es válido, proceder con la actualización
        if is_valid:
            logging.info("PoS: Actualizando la lista de participantes (stakes)...")
            
            # Ahora le pasamos el 'validated_stakes' (Dict[str, int])
            # Esto corrige el error de tu otra imagen (image_1ed866.png)
            self.update_stakes(validated_stakes) 
        else:
            logging.error("PoS: No se pudo actualizar la lista de stakes debido a datos inválidos.")
    
    def update_stakes(self, stakes_dict: Dict[str, int]):
        self._stakes = stakes_dict
        self._staker_addresses = sorted(list(self._stakes.keys())) 
        self._total_stake = sum(self._stakes.values())
        logging.info(f"PoS: Stakes actualizados. Stakers: {len(self._staker_addresses)}, Stake Total: {self._total_stake}")
'''