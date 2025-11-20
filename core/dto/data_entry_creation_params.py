# network_of_interactive_nodes/core/dto/data_entry_creation_params.py
'''
class DataEntryCreationParams:
    Agrupa todos los datos *crudos* necesarios por la Factory.

    Attributes:
            source_id      (str):                    Identificador de la fuente (sensor, app, nodo).
            data_type      (str):                    Tipo de dato (temperatura, humedad, etc.).
            value          (bytes):                  Contenido principal en binario (lectura o dato cifrado).
            previous_hash  (Optional[str]):          Hash previo (hex) opcional.
            nonce          (Optional[int]):          Nonce opcional (si es provisto externamente).
            metadata       (Optional[Dict[str, Any]]): Metadatos opcionales.
'''

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen = True, slots = True)
class DataEntryCreationParams:
    source_id: str
    data_type: str
    value: bytes
    previous_hash: Optional[str] = None
    nonce: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None