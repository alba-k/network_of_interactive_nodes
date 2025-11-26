# network_of_interactive_nodes/core/config.py
'''
class Config:
    Centraliza TODAS las constantes y políticas de la red.
    
    Beneficio: Permite ajustar la red (ej. hacerla más rápida para demos) 
    sin tocar el código fuente de los servicios.
'''
'''
class Config:
    # --- RED P2P (Network) ---
    # Límite de seguridad anti-DoS (2 MB)
    NETWORK_MAX_PAYLOAD_SIZE: int = 2 * 1024 * 1024 
    # Puerto por defecto si no se especifica
    NETWORK_DEFAULT_PORT: int = 8000
    # Tiempo de espera al iniciar para conectar seeds
    NETWORK_STARTUP_DELAY: int = 2

    # --- CONSENSO (Consensus) ---
    # Versión del protocolo
    PROTOCOL_VERSION: int = 1
    # Ajuste de dificultad: Tiempo esperado por bloque (60 segundos)
    # Tip: Bájalo a 10 segundos para demos en clase.
    BLOCK_TIME_TARGET_SEC: int = 60 
    # Cada cuántos bloques se recalcula la dificultad (10 bloques)
    DIFFICULTY_ADJUSTMENT_INTERVAL: int = 10
    
    # --- VALIDACIÓN (Validation) ---
    # Tolerancia de tiempo futuro para bloques (2 horas)
    BLOCK_MAX_FUTURE_TIME_SEC: int = 7200 

    # --- MEMPOOL (Memory Pool) ---
    # Tiempo de vida de una transacción en memoria (14 días)
    MEMPOOL_EXPIRY_SEC: int = 14 * 24 * 60 * 60 
    # Límite de transacciones en mempool (Protección DoS adicional)
    MEMPOOL_MAX_SIZE: int = 50000

    # Factor de amortiguación para evitar cambios bruscos de dificultad (4x)
    DIFFICULTY_CLAMP_FACTOR: int = 4

    # Nonce maximo
    MAX_NONCE: int = 4294967295
    '''

# config.py - MODO DEMO RÁPIDO

class Config:
    # --- RED P2P ---
    NETWORK_MAX_PAYLOAD_SIZE: int = 2 * 1024 * 1024 
    NETWORK_DEFAULT_PORT: int = 8000
    NETWORK_STARTUP_DELAY: int = 2

    # --- CONSENSO (Ajustado para DEMO) ---
    PROTOCOL_VERSION: int = 1
    
    # [CAMBIO] Tiempo esperado por bloque: 10 segundos (muy rápido)
    # Esto hace que la dificultad baje rápido si tardas mucho.
    BLOCK_TIME_TARGET_SEC: int = 10 
    
    DIFFICULTY_ADJUSTMENT_INTERVAL: int = 10
    
    # --- VALIDACIÓN ---
    BLOCK_MAX_FUTURE_TIME_SEC: int = 7200 

    # --- MEMPOOL ---
    MEMPOOL_EXPIRY_SEC: int = 14 * 24 * 60 * 60 
    MEMPOOL_MAX_SIZE: int = 50000

    DIFFICULTY_CLAMP_FACTOR: int = 4
    
    # Límite de intentos de hash por bloque
    MAX_NONCE: int = 4294967295