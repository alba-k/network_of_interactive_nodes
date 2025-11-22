# network_of_interactive_nodes/core/hashing/block_hasher.py
'''
class BlockHasher:
    Contiene la lógica pura para hashear la cabecera de un Bloque (Doble SHA-256).

    *** OPTIMIZACIÓN DE RENDIMIENTO: Usa 'struct' (Binario) en lugar de JSON. ***
    Esto aumenta drásticamente la velocidad de minado (Hashrate).

    Methods:
        calculate(dto: BlockHashingData) -> str: Calcula el hash doble SHA-256.
            1. Preparar datos binarios (convertir hex a bytes).
            2. Empaquetar en estructura binaria fija (Little Endian).
            3. Doble Hashing SHA-256.
            4. Retornar hash hexadecimal.
'''

import hashlib
import struct
from binascii import unhexlify

# Importaciones de la arquitectura
from core.dto.block_hashing_data import BlockHashingData

class BlockHasher:

    # Definición de la Estructura Binaria (Little Endian '<')
    # Q = Index (unsigned long long, 8 bytes)
    # d = Timestamp (double float, 8 bytes)
    # 32s = Previous Hash (32 bytes raw)
    # 4s = Bits (4 bytes raw - Dificultad compacta)
    # 32s = Merkle Root (32 bytes raw)
    # Q = Nonce (unsigned long long, 8 bytes)
    _STRUCT_FORMAT: str = '<Qd32s4s32sQ'

    @staticmethod
    def calculate(dto: BlockHashingData) -> str:
        
        # 1. Preparación de datos (Conversión Hex -> Bytes)
        # Si es el bloque Génesis, previous_hash es None, usamos 32 bytes vacíos.
        try:
            prev_hash_bytes: bytes = unhexlify(dto.previous_hash) if dto.previous_hash else b'\x00' * 32
            merkle_bytes: bytes = unhexlify(dto.merkle_root)
            bits_bytes: bytes = unhexlify(dto.bits)
        except Exception:
            # Fallback defensivo por si los datos no son hex válidos (aunque no debería pasar)
            # Esto mantiene la compatibilidad en caso de datos corruptos, pero rompe el consenso.
            raise ValueError("BlockHasher: Datos de cabecera corruptos (No son Hexadecimal válido).")

        # 2. Empaquetado Binario (Extremadamente rápido)
        header_bytes: bytes = struct.pack(
            BlockHasher._STRUCT_FORMAT,
            dto.index,
            float(dto.timestamp),
            prev_hash_bytes,
            bits_bytes,
            merkle_bytes,
            dto.nonce
        )

        # 3. Doble Hashing (Bitcoin Standard)
        first_hash_bytes: bytes = hashlib.sha256(header_bytes).digest()
        second_hash_hex: str = hashlib.sha256(first_hash_bytes).hexdigest()
        
        return second_hash_hex