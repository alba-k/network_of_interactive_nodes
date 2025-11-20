# network_of_interactive_nodes/core/dto/api/data_submission.py
'''
class DataSubmission(BaseModel):
    Define la estructura JSON esperada por la API para recibir un dato de un dispositivo externo.

    Attributes:
        source_id (str):              Identificador único del dispositivo.
        data_type (str):              Tipo de dato enviado.
        value     (str):              Los bytes crudos del dato, codificados como un string en Base66 (Base64).
        nonce     (Optional[int]):    Un número opcional usado una sola vez.
        metadata  (Optional[Dict]):   Metadatos adicionales en formato JSON.
'''

from pydantic import BaseModel
from typing import Optional, Dict, Any

class DataSubmission(BaseModel):
    source_id: str
    data_type: str
    value: str  
    nonce: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None