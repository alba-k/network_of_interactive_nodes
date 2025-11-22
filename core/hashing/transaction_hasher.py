# network_of_interactive_nodes/core/hashing/transaction_hasher.py
'''
class TransactionHasher:
    Contiene la lógica pura para hashear una Transaction.

    *** OPTIMIZACIÓN: Usa Binario (struct) en lugar de JSON para máximo rendimiento. ***

    Methods:
        calculate(dto: TransactionHashingData) -> str: Calcula un hash SHA-256 determinista.
            1. Empaquetar Timestamp (8 bytes).
            2. Convertir y concatenar los hashes de las entradas (raw bytes).
            3. Calcular SHA-256 sobre el buffer binario resultante.
            4. Retornar el hash final hexadecimal.
'''

import struct
import hashlib
from binascii import unhexlify

# Importaciones de la arquitectura
from core.dto.transaction_hashing_data import TransactionHashingData

class TransactionHasher:

    # Formato para el Timestamp (Double Float - Little Endian)
    _TIMESTAMP_FORMAT: str = '<d'

    @staticmethod
    def calculate(dto: TransactionHashingData) -> str:
        
        # 1. Iniciar el payload con el Timestamp (8 bytes)
        payload: bytes = struct.pack(TransactionHasher._TIMESTAMP_FORMAT, float(dto.timestamp))

        # 2. Concatenar los hashes de las entradas (DataEntries)
        # Convertimos de Hex String (64 chars) a Raw Bytes (32 bytes) para ahorrar espacio y CPU
        for entry in dto.entries:
            try:
                # Asumimos que data_hash es un hex válido SHA256
                entry_bytes = unhexlify(entry.data_hash)
                payload += entry_bytes
            except Exception:
                # Si el hash de la entrada está corrupto, lo tratamos como ceros (Defensivo)
                # Esto asegura que el hasher no rompa el flujo, aunque la TX será inválida después.
                payload += b'\x00' * 32

        # 3. Hashing SHA-256 puro sobre el buffer binario
        hash_object = hashlib.sha256(payload)
        hex_digest: str = hash_object.hexdigest()
        
        return hex_digest