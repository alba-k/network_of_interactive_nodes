# network_of_interactive_nodes/core/factories/data_entry_factory.py
'''
class DataEntryFactory:
    Ensamblar y crear objetos DataEntry inmutables.
    
    Methods:
        create(DataEntryCreationParams) -> DataEntry: Crea un nuevo objeto DataEntry con un hash válido.
            1. Generar valores por defecto (timestamp, nonce, metadata).
            2. Ensamblar el DTO para el hasher.
            3. Llamar al Hasher para calcular el hash.
            4. Instanciar el DataEntry final.
            5. Devolver la instancia creada.
'''

from typing import Dict, Any
import time

# Importaciones de la arquitectura
from core.hashing.data_entry_hasher import DataEntryHasher
from core.dto.data_entry_hashing_data import DataEntryHashingData
from core.models.data_entry import DataEntry
from core.dto.data_entry_creation_params import DataEntryCreationParams

class DataEntryFactory:

    @staticmethod
    def create( params: DataEntryCreationParams) -> DataEntry:

        timestamp: float = time.time()
        final_nonce: int = params.nonce if params.nonce is not None else 0
        final_metadata: Dict[str, Any] = params.metadata if params.metadata is not None else {}

        hashing_dto: DataEntryHashingData = DataEntryHashingData(
            source_id = params.source_id,
            data_type = params.data_type,
            value_bytes = params.value,
            timestamp = timestamp,
            nonce = final_nonce,
            previous_hash_hex = params.previous_hash,
            metadata = final_metadata
        )

        calculated_hash: str = DataEntryHasher.calculate(hashing_dto)

        new_data_entry: DataEntry = DataEntry(
            source_id = params.source_id,
            data_type = params.data_type,
            value = params.value,
            timestamp = timestamp,
            previous_hash = params.previous_hash,
            nonce = final_nonce,
            metadata = final_metadata,
            data_hash = calculated_hash 
        )

        return new_data_entry