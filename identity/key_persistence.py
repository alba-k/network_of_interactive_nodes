# network_of_interactive_nodes/identity/key_persistence.py
'''
class KeyPersistence:
    Herramienta estática para guardar y cargar claves del disco.
    Soporta formatos .pem (Estándar) y .txt (Hexadecimal para portabilidad).

    Methods:
        save_key_to_file(key: EccKey, filepath: str): 
            Guarda la clave privada en formato PEM en el disco.
            1. Exportar la clave a formato PEM.
            2. Abrir el archivo y escribir los datos.
            3. Registrar el log de éxito.

        ensure_key_exists(filepath: str) -> EccKey: 
            Carga la clave inteligente:
            1. Verificar si el archivo PEM existe.
            2. Si existe: Carga la clave desde el archivo PEM.
            3. Si no existe: Genera una clave nueva y la guarda como PEM.
'''

import os
import logging
from Crypto.PublicKey import ECC
from Crypto.PublicKey.ECC import EccKey

from identity.key_factory import KeyFactory

class KeyPersistence:

    @staticmethod
    def save_key_to_file(key: EccKey, filepath: str) -> None:
        try:
            pem_data = key.export_key(format = 'PEM')
            
            with open(filepath, 'wt') as f:
                f.write(pem_data)
            
            logging.info(f'''Seguridad: Clave privada guardada en '{filepath}'.''')
        except Exception as e:
            logging.error(f'''Seguridad: Error guardando clave: {e}''')
            raise

    @staticmethod
    def ensure_key_exists(filepath: str = 'mi_clave_privada.pem') -> EccKey:
        
        if os.path.exists(filepath):
            logging.warning(f'''Identidad: Clave existente '{filepath}' detectada. Cargando...''')
            
            try:
                with open(filepath, 'rt') as f:
                    content = f.read().strip()
        
                return ECC.import_key(content)

            except ValueError as e:
                logging.error(f'''Identidad: Archivo '{filepath}' corrupto o no es formato PEM válido. {e}''')
                raise
        else:
            logging.warning(f'Identidad: No se encontró clave principal. Creando nueva identidad...')
            new_key = KeyFactory.generate_private_key()
            KeyPersistence.save_key_to_file(new_key, filepath)
            return new_key