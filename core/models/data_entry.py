# network_of_interactive_nodes/core/models/data_entry.py
'''
class DataEntry:
    Representa un registro individual.

    Attributes:
        source_id       (str):              Identificador de la fuente (sensor, app, nodo)
        data_type       (str):              Tipo de dato (temperatura, humedad, etc.)
        value           (bytes):            Contenido principal en binario (lectura o dato cifrado)
        timestamp       (float):            Marca de tiempo UNIX de la creación
        previous_hash   (Optional[str]):    Hash previo (hex) opcional para encadenamiento
        nonce           (int):              Número único para garantizar unicidad
        metadata        (Dict[str, Any]):   Información adicional (ubicación, versión, etc.)
        data_hash       (str):              SHA-256 (hex) de los contenidos (calculado por la Factory)
'''

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen=True, slots=True)
class DataEntry:
    source_id: str
    data_type: str
    value: bytes
    timestamp: float
    previous_hash: Optional[str] 
    nonce: int
    metadata: Dict[str, Any]
    data_hash: str