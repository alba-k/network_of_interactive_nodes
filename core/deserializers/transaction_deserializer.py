# network_of_interactive_nodes/core/deserializers/transaction_deserializer.py
'''
class TransactionDeserializer:
    Contiene la lógica pura para deserializar un dict a una Transaction.

    Methods:
        from_dict(data: dict) -> Transaction: Reconstruye una Transaction desde un diccionario.
            1. Deserializar la lista de DataEntry (delegando a DataEntryDeserializer).
            2. Extraer los datos raíz de la transacción (timestamp, hash, signature).
            3. Ensamblar el DTO (TransactionHashingData) para recalcular el hash.
            4. Llamar al Hasher para recalcular el hash.
            5. Verificar la integridad (hash almacenado vs. hash recalculado).
            6. Construir el objeto final
            7. Retornar el objeto reconstruido  
'''

from typing import Any, List, Dict, Optional

# Importaciones de la arquitectura
from core.models.transaction import Transaction
from core.models.data_entry import DataEntry
from core.hashing.transaction_hasher import TransactionHasher
from core.dto.transaction_hashing_data import TransactionHashingData
from core.deserializers.data_entry_deserializer import DataEntryDeserializer

class TransactionDeserializer:

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Transaction:

        try:
            entries: List[DataEntry] = [
                DataEntryDeserializer.from_dict(entry_data)
                for entry_data in data['entries']
            ]

            timestamp: float = data['timestamp']
            tx_hash_stored: str = data['tx_hash']
            signature: Optional[str] = data.get('signature')

            hashing_dto: TransactionHashingData = TransactionHashingData(
                entries=entries, 
                timestamp=timestamp
            )

            calculated_hash: str = TransactionHasher.calculate(hashing_dto)

            if calculated_hash != tx_hash_stored:
                raise ValueError('Corrupción de datos: El hash de la transacción no coincide.')

            reconstructed_Transaction: Transaction = Transaction(
                entries = entries,
                timestamp = timestamp,
                signature = signature,
                tx_hash = tx_hash_stored
            )
  
            return reconstructed_Transaction

        except KeyError as e:
            raise ValueError(f'Dato corrupto en Transaction JSON (falta clave: {e})')