# network_of_interactive_nodes/core/builders/transaction_builder.py
'''
class TransactionBuilder:
    Orquesta el ciclo de vida completo de la creación de una transacción.

    Methods::
        build(entries, timestamp, private_key, public_key) -> Transaction: 
            Construye, firma y verifica una Transaction.
'''

import logging
from typing import List, Any, TYPE_CHECKING
from Crypto.PublicKey.ECC import EccKey

# Importaciones de la Arquitectura
from core.models.data_entry import DataEntry
from core.models.transaction import Transaction
from core.dto.transaction_creation_params import TransactionCreationParams
from core.dto.transaction_hashing_data import TransactionHashingData
from core.factories.transaction_factory import TransactionFactory
from core.hashing.transaction_hasher import TransactionHasher
from core.security.transaction_signer import TransactionSigner
from core.validators.transaction_verifier import TransactionVerifier
from core.validators.transaction_validator import TransactionValidator

if TYPE_CHECKING:
    EccKeyType = Any
else:
    EccKeyType = EccKey

class TransactionBuilder:

    @staticmethod
    def build(
        entries: List[DataEntry], 
        timestamp: float, 
        private_key: EccKeyType,
        public_key: EccKeyType
    ) -> Transaction:

        fee: int = len(entries) # 1 unidad de fee por cada entrada de datos
        size_bytes: int = sum(len(entry.value) for entry in entries)
        fee_rate: float = (fee / size_bytes) if size_bytes > 0 else 0.0

        hashing_dto: TransactionHashingData = TransactionHashingData(
            entries = entries, 
            timestamp = timestamp
        )
        
        tx_hash: str = TransactionHasher.calculate(hashing_dto)
        signature: str = TransactionSigner.sign(private_key, tx_hash)
        
        creation_params: TransactionCreationParams = TransactionCreationParams(
            entries = entries,
            timestamp = timestamp,
            signature = signature,
            fee = fee,
            size_bytes = size_bytes,
            fee_rate = fee_rate
        )

        tx: Transaction = TransactionFactory.create(creation_params)

        if not TransactionValidator.verify(tx):
            logging.error(f'TransactionBuilder: Error de integridad interna en TX {tx.tx_hash[:8]}.')
            raise ValueError('Error de integridad: El hash de la transacción falló.')

        if tx.signature is None:
            raise ValueError('Error de seguridad: La transacción fue creada sin firma.')

        is_valid_sig = TransactionVerifier.verify(public_key, tx.tx_hash, tx.signature)
        
        if not is_valid_sig:
            logging.critical(f'TransactionBuilder: Firma generada INVÁLIDA para TX {tx.tx_hash[:8]}. Revise claves.')
            raise ValueError('Error de seguridad: La firma de la transacción es inválida (Fallo al verificar recién creada).')

        return tx