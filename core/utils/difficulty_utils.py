'''
# network_of_interactive_nodes/core/utils/difficulty_utils.py
''
class DifficultyUtils:
    Contiene la lógica "helper" (de utilidad) pura para manejar la dificultad (Bits y Target).
    
    Constants:
        MAX_TARGET: (int) Es 0x1d00ffff en formato 'bits'  

    Methods:
        bits_to_target(bits: str) -> int:
            1. Extraer el exponente (exp) y la mantisa (mant) del string 'bits'.
            2. Calcular el target usando la fórmula (mant * 2^(8 * (exp - 3))).
            3. Retornar el target (int).

        target_to_bits(target: int) -> str:
            1. Convertir a bytes (big-endian)
            2. El 'exp' (exponente) es la longitud en bytes
            3. La 'mant' (mantisa) son los primeros 3 bytes
            4. Manejar desbordamiento (si los primeros 3 bytes son demasiado grandes)
            5. Formatear como hex string
''

class DifficultyUtils:

    # Es 0x1d00ffff en formato 'bits'
    MAX_TARGET: int = 0x00FFFF0000000000000000000000000000000000000000000000000000000000

    @staticmethod
    def bits_to_target(bits: str) -> int:
        try:
            exp = int(bits[:2], 16)
            mant = int(bits[2:], 16)
            target = mant * (1 << (8 * (exp - 3)))
            return target
        except (ValueError, TypeError):
            raise ValueError(f"Formato de 'bits' de dificultad inválido: {bits}")

    @staticmethod
    def target_to_bits(target: int) -> str:

        if target < 0:
            raise ValueError('Target no puede ser negativo.')
        if target == 0:
            return '00000000' # Aunque 0 no debería ser un target

        # (target.bit_length() + 7) // 8 calcula el número de bytes
        target_bytes = target.to_bytes((target.bit_length() + 7) // 8, 'big')

        exp = len(target_bytes)
         
        # Rellenamos con ceros a la izquierda si es necesario
        if exp > 3:
            mant_bytes = target_bytes[:3]
        else:
            mant_bytes = target_bytes.rjust(3, b'\x00')
            
        # Si el bit más significativo (0x800000) está puesto, significa que necesitamos un byte más para el exponente.
        mant_int = int.from_bytes(mant_bytes, 'big')
        if mant_int & 0x800000:
            mant_bytes = b'\x00' + mant_bytes[:2] # Desplazar a la derecha
            exp += 1

        mant_hex = mant_bytes.hex().zfill(6)
        exp_hex = f'{exp:02x}'
        
        return f'{exp_hex}{mant_hex}'
        '''
# core/utils/difficulty_utils.py
'''
class DifficultyUtils:
    Modo DEMO ACTIVADO: Dificultad extremadamente baja para minar en segundos.
'''

class DifficultyUtils:

    # --- CAMBIO CRÍTICO: MODO DEMO ---
    # Antes: 0x00FFFF... (Difícil)
    # Ahora: 0xFFFFFF... (Muy Fácil - Acepta casi todo)
    MAX_TARGET: int = 0xFFFFFF0000000000000000000000000000000000000000000000000000000000

    @staticmethod
    def bits_to_target(bits: str) -> int:
        try:
            exp = int(bits[:2], 16)
            mant = int(bits[2:], 16)
            target = mant * (1 << (8 * (exp - 3)))
            return target
        except (ValueError, TypeError):
            # Si hay error, devolvemos la dificultad más fácil para no trabar la demo
            return DifficultyUtils.MAX_TARGET

    @staticmethod
    def target_to_bits(target: int) -> str:
        if target < 0:
            raise ValueError('Target no puede ser negativo.')
        if target == 0:
            return '00000000'

        target_bytes = target.to_bytes((target.bit_length() + 7) // 8, 'big')
        exp = len(target_bytes)
         
        if exp > 3:
            mant_bytes = target_bytes[:3]
        else:
            mant_bytes = target_bytes.rjust(3, b'\x00')
            
        mant_int = int.from_bytes(mant_bytes, 'big')
        if mant_int & 0x800000:
            mant_bytes = b'\x00' + mant_bytes[:2]
            exp += 1

        mant_hex = mant_bytes.hex().zfill(6)
        exp_hex = f'{exp:02x}'
        
        return f'{exp_hex}{mant_hex}'