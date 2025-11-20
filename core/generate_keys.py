# network_of_interactive_nodes/generate_keys.py
'''
Herramienta de "Día 1" (Creación).

Este script se ejecuta UNA SOLA VEZ para generar los archivos
de clave (.pem y .pub) para todos los nodos que participarán
en la red.

Estos archivos son la "identidad permanente" de los nodos.
'''

import logging
import os
from Crypto.PublicKey import ECC

# --- Configuración de Identidades ---
GATEWAY_ID = "device_sensor_001"
MINER_ID = "miner_node_555"

# --- Carpeta de Destino ---
KEY_PATH = "config_keys" 
if not os.path.exists(KEY_PATH):
    os.makedirs(KEY_PATH)

logging.basicConfig(level=logging.INFO, format='%(message)s')

def create_and_save_keys(key_name: str):
    '''
    Herramienta interna: Genera y Guarda el par de claves.
    '''
    logging.info(f"Generando par de claves para {key_name}...")
    
    # 1. CREAR la clave privada (El "PIN secreto")
    private_key = ECC.generate(curve='P-256')
    
    # 2. DERIVAR la clave pública (La "Plantilla")
    public_key = private_key.public_key()
    
    # 3. GUARDAR ambas en archivos
    priv_path = os.path.join(KEY_PATH, f"{key_name}_key.pem")
    pub_path = os.path.join(KEY_PATH, f"{key_name}_key.pub")

    try:
        # Guardar Clave Privada (Formato PEM)
        with open(priv_path, "wb") as f:
            f.write(private_key.export_key(format="PEM").encode('utf-8'))
            
        # Guardar Clave Pública (Formato PEM)
        with open(pub_path, "wb") as f:
            f.write(public_key.export_key(format="PEM").encode('utf-8'))
            
        logging.info(f" -> Claves guardadas en {priv_path} y {pub_path}\n")
        
    except IOError as e:
        logging.error(f"Error guardando claves para {key_name}: {e}")

if __name__ == "__main__":
    logging.info("--- Iniciando Generador de Claves Permanentes ---")
    create_and_save_keys(GATEWAY_ID)
    create_and_save_keys(MINER_ID)
    logging.info("--- Generación de claves completada ---")