# network_of_interactive_nodes/core/p2p/p2p_message_deserializer.py
'''
class P2PMessageDeserializer:
    Contiene la lógica pura para deserializar un 'Message' P2P (bytes crudos) de vuelta a un DTO 'Message'.

    Attributes:
        PAYLOAD_MAPPER (Dict[str, Type[Any]]): 
            Un mapa estático que asocia 'commands' (str) con sus clases DTO de payload.

    Methods:
        deserialize(data: bytes) -> Message: Toma bytes crudos de la red, valida el paquete completo y lo convierte en un objeto 'Message' estructurado con el payload DTO correcto.
            1. Desempaqueta el Header binario (command, size, checksum).
            2. Extrae los bytes del payload y valida su tamaño.
            3. Valida el Checksum (doble SHA-256) para integridad.
            4. Decodifica los bytes del comando y limpia el padding nulo.
            5. Usa el PAYLOAD_MAPPER para encontrar la clase DTO correspondiente.
            6. Deserializa los bytes del payload (JSON) en una instancia del DTO.
            7. Construye y retorna el objeto 'Message' final.
'''

'''
(Docstring sin cambios)
'''

import json
import struct 
import hashlib
from typing import Dict, Type, Any, List # <-- Añadido List

# Importaciones de la Arquitectura 
from core.p2p.message import Message
from core.p2p.p2p_message_serializer import P2PMessageSerializer

# Importaciones de Payloads (DTOs) 
from core.p2p.payloads.version_payload import VersionPayload
from core.p2p.payloads.inv_payload import InvPayload
from core.p2p.payloads.get_data_payload import GetDataPayload
from core.p2p.payloads.block_payload import BlockPayload
from core.p2p.payloads.tx_payload import TxPayload
from core.p2p.payloads.get_headers_payload import GetHeadersPayload
from core.p2p.payloads.headers_payload import HeadersPayload

# Importar el DTO Anidado 
from core.p2p.payloads.inv_vector import InvVector

class P2PMessageDeserializer:

    PAYLOAD_MAPPER: Dict[str, Type[Any]] = {
        'version': VersionPayload,
        'inv': InvPayload,
        'getdata': GetDataPayload,
        'block': BlockPayload,
        'tx': TxPayload,
        'getheaders': GetHeadersPayload,
        'headers': HeadersPayload
    }

    @staticmethod
    def deserialize(data: bytes) -> Message:
    
        try:
            header_bytes: bytes = data[:P2PMessageSerializer.HEADER_SIZE]
            header_format: str = P2PMessageSerializer.HEADER_FORMAT
            unpacked_data: tuple[bytes, int, bytes] = struct.unpack(header_format, header_bytes)
            command_bytes: bytes = unpacked_data[0]
            payload_size: int = unpacked_data[1] 
            checksum_bytes: bytes = unpacked_data[2]
        except struct.error:
            raise ValueError('Error P2P: Paquete de red incompleto (Header).')

        payload_bytes = data[P2PMessageSerializer.HEADER_SIZE : P2PMessageSerializer.HEADER_SIZE + payload_size]
        
        if len(payload_bytes) != payload_size:
            raise ValueError('Error P2P: Tamaño de payload no coincide (Corrupto).')

        # (Validación de Checksum - Correcta)
        first_hash_obj = hashlib.sha256(payload_bytes)
        first_hash_bytes: bytes = first_hash_obj.digest()
        second_hash_obj = hashlib.sha256(first_hash_bytes) 
        second_hash_bytes: bytes = second_hash_obj.digest()
        calculated_checksum: bytes = second_hash_bytes[:4]
    
        if calculated_checksum != checksum_bytes:
            raise ValueError('Error P2P: Checksum de payload falló (Corrupto).')

        command_with_padding: str = command_bytes.decode('utf-8')
        command: str = command_with_padding.strip('\x00')

        payload_class = P2PMessageDeserializer.PAYLOAD_MAPPER.get(command)
        
        if not payload_class:
            raise ValueError(f'''Error P2P: Comando '{command}' desconocido.''')

        try:
            payload_json_str: str = payload_bytes.decode('utf-8')
            payload_dict: Dict[str, Any] = json.loads(payload_json_str)

        except json.JSONDecodeError:
            raise ValueError(f'''Error P2P: Payload JSON malformado para '{command}'.''')

        if command == 'inv' or command == 'getdata':
            inventory_data: List[Dict[str, Any]] = payload_dict.get('inventory', [])
            inventory_objects: List[InvVector] = []
            
            for item_dict in inventory_data:
                
                item_type = item_dict.get('type')
                item_hash = item_dict.get('hash')
                
                if item_type is None or item_hash is None:
                    continue # Saltar este item corrupto

                inv_obj = InvVector(type = item_type, hash = item_hash)

                
                inventory_objects.append(inv_obj)
            
            payload_dict['inventory'] = inventory_objects

        try:
            payload_dto = payload_class(**payload_dict)
            
        except (TypeError, AttributeError) as e: 
            raise ValueError(f'''Error P2P: Datos de payload incorrectos para '{command}'. {e}''')

        final_message = Message(command = command, payload = payload_dto)
        return final_message