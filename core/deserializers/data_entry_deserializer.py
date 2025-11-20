# network_of_interactive_nodes/core/deserializers/data_entry_deserializer.py
'''
class DataEntryDeserializer:
    Convierte diccionarios (JSON-friendly) de vuelta a DataEntry.

    Methods:
        from_dict(data: Dict) -> DataEntry: Convierte un diccionario a un DataEntry, validando el hash.
            1. Convertir 'value' (hex str) de nuevo a bytes.
            2. Obtener los hashes (data_hash y previous_hash).
            3. Ensamblar el DTO (DataEntryHashingData) con los datos leídos.
            4. Recalcular el hash usando el DataEntryHasher.
            5. VERIFICAR INTEGRIDAD (comparar hash calculado con hash leído).
            6. Construirel objeto DataEntry final.
            7. Retornar el objeto reconstruido
'''

import binascii
from typing import Dict, Any, Optional

# Importaciones de la arquitectura
from core.models.data_entry import DataEntry
from core.hashing.data_entry_hasher import DataEntryHasher
from core.dto.data_entry_hashing_data import DataEntryHashingData

class DataEntryDeserializer:

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> DataEntry:
        try:
            value_bytes: bytes = bytes.fromhex(data['value'])
            
            data_hash_hex: str = data['data_hash']
            prev_hash_hex: Optional[str] = data.get('previous_hash')
            
            hashing_dto: DataEntryHashingData = DataEntryHashingData(
                source_id = data['source_id'],
                data_type = data['data_type'],
                value_bytes = value_bytes,
                timestamp = data['timestamp'],
                nonce = data['nonce'],
                previous_hash_hex = prev_hash_hex,
                metadata = data['metadata']
            )

            calculated_hash_hex: str = DataEntryHasher.calculate(hashing_dto)
            
            if calculated_hash_hex != data_hash_hex:
                raise ValueError('Corrupción de datos: El hash del DataEntry no coincide.')
                
            reconstructed_entry: DataEntry = DataEntry(
                source_id = data['source_id'],
                data_type = data['data_type'],
                value = value_bytes,
                timestamp = data['timestamp'],
                previous_hash = prev_hash_hex,
                nonce = data['nonce'],
                metadata = data['metadata'],
                data_hash = data_hash_hex
            )
            
            return reconstructed_entry
        
        except KeyError as e:
            raise ValueError(f'Dato corrupto en DataEntry JSON (falta clave: {e})')
        except (binascii.Error, TypeError) as e:
            raise ValueError(f'Datos de DataEntry malformados (hex/tipo incorrecto): {e}')