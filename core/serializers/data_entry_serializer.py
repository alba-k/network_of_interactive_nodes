# network_of_interactive_nodes/core/serializers/data_entry_serializer.py
'''
class DataEntrySerializer:
    Convierte DataEntry a diccionarios (JSON-friendly).

    Methods:
        to_dict(entry: DataEntry) -> Dict: Convierte un DataEntry a un diccionario.
            1. Usar 'asdict' para la conversión base del dataclass.
            2. Convertir el campo 'value' (bytes) a un string hexadecimal.
            3. Retornar el diccionario modificado.
'''

from core.models.data_entry import DataEntry
from typing import Dict, Any
from dataclasses import asdict

class DataEntrySerializer:
    @staticmethod
    def to_dict(entry: DataEntry) -> Dict[str, Any]:
        entry_dict: Dict[str, Any] = asdict(entry)
        value_hex: str = entry.value.hex()
        entry_dict['value'] = value_hex
        return entry_dict