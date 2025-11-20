# network_of_interactive_nodes/core/security/ecdsa_private_key_loader.py
'''
class EcdsaPrivateKeyLoader(IKeyLoader):
    Carga una clave privada ECDSA desde un archivo PEM.

    Methods:
        load(path: str) -> EccKey:
            1. Verificar que el archivo exista.
            2. Leer los bytes del archivo de clave.
            3. Importar la clave ECDSA.
            4. Verificar que sea una clave privada.
            5. Retornar el objeto clave.
'''

import os
from Crypto.PublicKey import ECC
from Crypto.PublicKey.ECC import EccKey

# Importación del Contrato (Interfaz Unificada)
from core.interfaces.i_key_loader import IKeyLoader

class EcdsaPrivateKeyLoader(IKeyLoader):

    @staticmethod
    def load(path: str) -> EccKey:
        
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f'Archivo de clave no encontrado: {path}')
            
            with open(path, 'rb') as f:
                key_bytes: bytes = f.read()

            key_object: EccKey = ECC.import_key(key_bytes)
            
            if not key_object.has_private():
                raise ValueError(f'El archivo {path} no contiene una clave privada.')
            
            return key_object
        
        except (IOError, FileNotFoundError) as e:
            raise IOError(f'Error al leer el archivo de clave {path}: {e}')
        except ValueError as e:
            raise ValueError(f'Error al importar la clave {path} (formato inválido): {e}')