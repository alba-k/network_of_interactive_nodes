# network_of_interactive_nodes/core/security/ecdsa_public_key_loader.py
'''
class EcdsaPublicKeyLoader(IKeyLoader):
    Carga una clave pública ECDSA desde un archivo PEM.

    Methods:
        load(path: str) -> EccKey:
            1. Verificar que el archivo exista.
            2. Leer los bytes del archivo de clave.
            3. Importar la clave ECDSA (pública).
            4. Retornar el objeto clave.
'''

import os
from Crypto.PublicKey import ECC
from Crypto.PublicKey.ECC import EccKey

# Importación del Contrato (Interfaz Unificada) 
from core.interfaces.i_key_loader import IKeyLoader

class EcdsaPublicKeyLoader(IKeyLoader):

    @staticmethod
    def load(path: str) -> EccKey:
        
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f'Archivo de clave no encontrado: {path}')

            with open(path, 'rb') as f:
                key_bytes: bytes = f.read()

            key_object: EccKey = ECC.import_key(key_bytes)
            
            return key_object

        except (IOError, FileNotFoundError) as e:
            raise IOError(f'Error al leer el archivo de clave {path}: {e}')
        except ValueError as e:
            raise ValueError(f'Error al importar la clave {path} (formato inválido): {e}')