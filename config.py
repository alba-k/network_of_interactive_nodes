# config.py

'''
Archivo de Configuración Central para la Blockchain.
'''

# --- CONFIGURACIÓN DE LA RED ---
DEFAULT_PORT = 5001
# Lista de nodos pares iniciales con los que intentar conectar
PEERS: list[str] = list()

# --- CONFIGURACIÓN DE PERSISTENCIA ---
BLOCKCHAIN_FILE: str = 'blockchain_data.json'

# --- CONFIGURACIÓN DEL CONSENSO (PROOF OF WORK) ---
# Dificultad inicial de la red
INITIAL_DIFFICULTY: int = 4

# --- CONFIGURACIÓN DEL AJUSTE DE DIFICULTAD ---
# Cada cuántos bloques se debe reajustar la dificultad
DIFFICULTY_ADJUSTMENT_INTERVAL: int = 10

# El tiempo esperado para minar UN bloque
EXPECTED_BLOCK_TIME_SECONDS: int = 30  # segundos

# El tiempo total esperado para minar el intervalo completo de bloques
EXPECTED_INTERVAL_TIME: int = DIFFICULTY_ADJUSTMENT_INTERVAL * EXPECTED_BLOCK_TIME_SECONDS