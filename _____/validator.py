# validator.py (Versión Final Corregida)
'''
class Validator:
    Servicio especialista para validar la integridad de bloques, cadenas y transacciones.
    Es un servicio SILENCIOSO: solo retorna True o False.
'''

# --- Imports Limpios ---
from typing import List, Optional

# --- Imports de Arquitectura ---
from core.models.block import Block 
from core._____.i_consensus import IConsensus
from core.utils.crypto_utils import CryptoUtils # Importa la calculadora
from core.models.transaction import Transaction  # Importa la clase real

class Validator:

    # ================================== #
    # --- METODOS DE BLOQUE Y CADENA --- #
    # ================================== # 

    def is_block_valid( self, block: Block, previous_block: Optional[Block], consensus: IConsensus) -> bool:
        'Valida un bloque individual. SILENCIOSO: solo retorna True o False.'
        
        try:
            # 1. Validar si es Bloque Génesis o un bloque normal
            if previous_block is not None: 
                # --- Caso 1: Bloque Normal ---
                
                # 1a. --- verifica el índice sea consecutivo ---
                if block.index != previous_block.index + 1:
                    return False
                
                # 1b. --- verifica el enlace criptográfico ---
                if block.previous_hash != previous_block.hash: 
                    return False
            
            else: 
                # --- Caso 2: Bloque Génesis ---
                if block.index != 0:
                    return False

            # 2. --- Verifica la integridad del HASH (CRÍTICO) ---
            # (¿El hash declarado del bloque coincide con su contenido real?)
            calculated_hash = CryptoUtils.calculate_hash(
                index=block.index,
                timestamp=block.timestamp,
                previous_hash=block.previous_hash,
                merkle_root=block.merkle_root,
                difficulty=block.difficulty,
                nonce=block.nonce
            )
            if block.hash != calculated_hash:
                return False # ¡Hash corrupto o manipulado!
                
            # 3. --- DELEGA la validación de consenso ---
            if not consensus.validate(block):
                return False

        except Exception:
            return False # Fallo silencioso si algo inesperado ocurre

        return True

    def is_chain_valid(self, chain: List[Block], consensus: IConsensus) -> bool:
        'Valida la integridad de la cadena completa, incluyendo el Génesis.'
        
        if not chain: # Una cadena vacía no es válida
            return False

        previous_block: Optional[Block] = None
        
        for block in chain:
            # Llama a is_block_valid (ahora corregido) para cada uno
            if not self.is_block_valid(block, previous_block, consensus):
                return False
                
            previous_block = block
            
        return True # Si todos los bloques pasaron, la cadena es válida

    # ============================= #
    # --- MÉTODO DE TRANSACCIÓN --- #
    # ============================= #
    
    def is_transaction_valid(self, transaction: Transaction) -> bool:
        '''
        Valida una transacción ANTES de que entre a la Mempool.
        Verifica la firma digital y reglas básicas.
        '''
        
        try:
            # 1. --- Validación de Reglas de Negocio (Ejemplos) ---
            if transaction.amount <= 0:
                return False # No se pueden enviar 0 o menos
            
            if transaction.sender == transaction.recipient:
                return False # No se puede enviar a uno mismo (opcional)

            # 2. --- Validación Criptográfica (La parte CRÍTICA) ---
            
            if transaction.signature is None:
                return False # La transacción no está firmada

            # --- Recalcular el hash de los datos ---
            tx_hash = transaction.calculate_hash()
            
            # --- DELEGAR la verificación a CryptoUtils ---
            is_signature_valid = CryptoUtils.verify_signature(
                public_key_hex=transaction.sender,
                signature_hex=transaction.signature,
                data_hash=tx_hash
            )
            
            return is_signature_valid
        
        except AttributeError:
            # Si 'transaction' no era un objeto Transaction real
            return False
        except Exception:
            # Captura cualquier otro error
            return False