# network_of_interactive_nodes/core/managers/validation_manager.py
'''
class ValidationManager(IBlockValidatorRole):
    Implementa el "Rol" de validación de Consenso. 
    Es un "Gestor" (Capa 2) que se encarga *solo* de aplicar las reglas de negocio (Consenso).

    Attributes:
        _consensus_manager  (ConsensusManager):     Gestor que aplica las reglas de la cadena (PoW, dificultad).
        _mempool            (Mempool):              Gestor que almacena las transacciones pendientes.
        _public_key_map     (Dict[str, EccKey]):    Mapa de claves públicas para la verificación de firmas.

    Methods:
        validate_block_rules(block: Block) -> bool:
            1. Delega la validación completa del bloque al ConsensusManager.
            2. Si el bloque es válido y nuevo (is_new_block):
            3. Limpia el Mempool de las transacciones ya minadas.
            4. Retorna True (el bloque fue aceptado).

        validate_tx_rules(tx: Transaction) -> bool:
            1. Validar integridad del hash (Delega a TransactionValidator).
            2. Validar la firma (Delega a TransactionVerifier).
            3. Si es válida, añadirla al Mempool.
            4. Retorna True (la TX fue aceptada en la Mempool).
'''

import logging
from typing import Dict
from Crypto.PublicKey.ECC import EccKey

# Importaciones de Interfaces (Contratos) 
from core.interfaces.i_node_roles import IBlockValidatorRole

# Importaciones de Gestores (Estado) 
from core.consensus.consensus_manager import ConsensusManager
from core.mempool.mempool import Mempool

# Importaciones de Modelos (Datos) 
from core.models.block import Block
from core.models.transaction import Transaction

# Importaciones del Núcleo Estático (Herramientas) 
from core.validators.transaction_validator import TransactionValidator
from core.validators.transaction_verifier import TransactionVerifier

class ValidationManager(IBlockValidatorRole):
    def __init__(self, 
        consensus_manager: ConsensusManager, 
        mempool: Mempool, 
        public_key_map: Dict[str, EccKey]):
        
        self._consensus_manager = consensus_manager
        self._mempool = mempool
        self._public_key_map = public_key_map
        logging.info('Validation Manager (Gestor de Consenso) inicializado.')

    def validate_block_rules(self, block: Block) -> bool:

        is_new_block = self._consensus_manager.add_block(block, self._public_key_map)

        if is_new_block:
            logging.info(f'Consenso: Bloque {block.index} (hash: {block.hash[:6]}) aceptado.')
            self._mempool.remove_mined_transactions(block.data)
        return is_new_block

    def validate_tx_rules(self, tx: Transaction) -> bool:

        if not TransactionValidator.verify(tx):
            logging.warning(f'Consenso: TX {tx.tx_hash} rechazada (Integridad fallida).')
            return False
        
        if tx.signature is not None:
            if not tx.entries: 
                logging.warning(f'Consenso: TX {tx.tx_hash} rechazada (firmada pero sin entries).')
                return False
            
            owner_id = tx.entries[0].source_id
            public_key = self._public_key_map.get(owner_id)

            if not public_key or not TransactionVerifier.verify(public_key, tx.tx_hash, tx.signature):
                logging.warning(f'Consenso: TX {tx.tx_hash} rechazada (Firma inválida).')
                return False
            
        is_new_tx = self._mempool.add_transaction(tx)

        if is_new_tx:
            logging.info(f'Consenso: TX {tx.tx_hash[:6]} aceptada en Mempool.')

        return is_new_tx