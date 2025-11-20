# network_of_interactive_nodes/core/factories/transaction_factory.py
'''
class TransactionFactory:
    Ensambla y crea el objeto Transaction final.
    
    Methods:
        create(params: TransactionCreationParams) -> Transaction: Crea el objeto Transaction final.
            1. Ensamblar el DTO de hashing (TransactionHashingData).
            2. Calcular el hash de la transacción (delegando a TransactionHasher).
            3. Instanciar el modelo Transaction final con todos los datos.
            4. Retornar la instancia.
'''

# Importaciones de la arquitectura
from core.hashing.transaction_hasher import TransactionHasher
from core.dto.transaction_hashing_data import TransactionHashingData
from core.models.transaction import Transaction
from core.dto.transaction_creation_params import TransactionCreationParams

class TransactionFactory:

    @staticmethod
    def create(params: TransactionCreationParams) -> Transaction:

        hashing_dto: TransactionHashingData = TransactionHashingData(
            entries = params.entries,
            timestamp = params.timestamp
        )

        calculated_hash: str = TransactionHasher.calculate(hashing_dto)

        new_transaction: Transaction = Transaction(
            entries = params.entries,
            timestamp = params.timestamp,
            signature = params.signature,
            tx_hash = calculated_hash,
            fee = params.fee,
            size_bytes = params.size_bytes,
            fee_rate = params.fee_rate
        )
        
        return new_transaction