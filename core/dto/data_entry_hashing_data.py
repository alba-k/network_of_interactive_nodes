# network_of_interactive_nodes/core/dto/data_entry_hashing_data.py
'''
class DataEntryHashingData:
    Agrupa todos los campos que entran en el cálculo del hash.

    Attributes:
        source_id         (str):              Identificador de la fuente.
        data_type         (str):              Tipo de dato.
        value_bytes       (bytes):            Contenido principal en binario.
        timestamp         (float):            Marca de tiempo UNIX.
        nonce             (int):              Nonce utilizado.
        previous_hash_hex (Optional[str]):    Hash previo (hex).
        metadata          (Dict[str, Any]):   Metadatos.
'''

from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass(frozen = True, slots = True)
class DataEntryHashingData:
    source_id: str
    data_type: str
    value_bytes: bytes
    timestamp: float
    nonce: int
    previous_hash_hex: Optional[str]
    metadata: Dict[str, Any]