# network_of_interactive_nodes/core/validators/transaction_validator.py
'''
class TransactionValidator:
    Verifica la integridad de una Transaction (su hash y todos sus DataEntry).

    Methods:
        verify(tx: Transaction) -> bool: Ejecuta una validación completa de la transacción.
            1. Validar la integridad de cada DataEntry.
            2. Ensamblar el DTO (TransactionHashingData) para el hasher de la transacción.
            3. Llamar al Hasher para recalcular el hash de la transacción.
            4. Comparar el hash recalculado con el hash almacenado.
            5. Retornar True solo si AMBAS validaciones (entries y hash) son correctas.
'''

# Importaciones de la arquitectura
from core.models.transaction import Transaction
from core.hashing.transaction_hasher import TransactionHasher
from core.dto.transaction_hashing_data import TransactionHashingData
from core.validators.data_entry_validator import DataEntryValidator

class TransactionValidator:

    @staticmethod
    def verify(tx: Transaction) -> bool:

        entries_are_valid: bool = all(DataEntryValidator.verify(e) for e in tx.entries)
        
        hashing_dto: TransactionHashingData = TransactionHashingData(
            entries = tx.entries,
            timestamp = tx.timestamp
        )

        recalculated_hash: str = TransactionHasher.calculate(hashing_dto)
        tx_hash_is_valid: bool = (tx.tx_hash == recalculated_hash)
        return entries_are_valid and tx_hash_is_valid