# network_of_interactive_nodes/core/validators/data_entry_validator.py
'''
class DataEntryValidator:
    Verifica la integridad de un DataEntry existente.

    Methods:
        verify(entry: DataEntry) -> bool: Compara el hash almacenado vs. un hash recalculado.
            1. Ensamblar el DTO (DataEntryHashingData) con los datos del DataEntry.
            2. Llamar al Hasher para recalcular el hash.
            3. Comparar el hash recalculado con el hash almacenado en el entry.
            4. Retornar el resultado de la comparación (True/False).
'''

# Importac0iones de la arquitectura
from core.models.data_entry import DataEntry
from core.hashing.data_entry_hasher import DataEntryHasher
from core.dto.data_entry_hashing_data import DataEntryHashingData

class DataEntryValidator:

    @staticmethod
    def verify(entry: DataEntry) -> bool:

        hashing_dto: DataEntryHashingData = DataEntryHashingData(
            source_id = entry.source_id,
            data_type = entry.data_type,
            value_bytes = entry.value,
            timestamp = entry.timestamp,
            nonce = entry.nonce,
            previous_hash_hex = entry.previous_hash,
            metadata = entry.metadata   
        )

        recalculated_hash: str = DataEntryHasher.calculate(hashing_dto)
        is_valid: bool = (entry.data_hash == recalculated_hash)
        return is_valid