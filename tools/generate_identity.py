# network_of_interactive_nodes/tools/generate_identity.py
'''
Script: tools/generate_identity.py
----------------------------------------------------------------------
Propósito: Servicio de utilidad OFFLINE para la generación de identidad (Clave/Dirección).
           Genera una nueva clave privada y la guarda en disco para que el nodo la use después.

Responsabilidad: Actuar como "Composition Root" para el subsistema 'identity/'.

Pasos:
    1. Generar la clave privada (KeyFactory).
    2. Derivar la dirección (AddressFactory).
    3. Persistir la clave en un archivo (.pem) para uso futuro.
    4. Mostrar los resultados (Clave HEX y Dirección) al usuario.
----------------------------------------------------------------------
'''

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from identity.key_factory import KeyFactory
from identity.address_factory import AddressFactory
from identity.key_persistence import KeyPersistence

def main():
    print('--- GENERADOR DE IDENTIDAD (OFFLINE) ---')
    print('Generando par de claves criptográficas...')

    private_key = KeyFactory.generate_private_key()
    public_key = private_key.public_key()
    
    address = AddressFactory.generate_p2pkh(public_key)
    
    private_key_bytes = private_key.export_key(format = 'DER')
    private_key_hex = private_key_bytes.hex()

    print(f'\nNueva Identidad Creada (No Guardada):')
    print(f'\tDirección (Address): {address}')
    print(f'\tClave Privada (HEX): {private_key_hex}')

    filename = 'mi_billetera.pem'
    
    if os.path.exists(filename):
        print('\n!!! ALERTA DE SEGURIDAD !!!')
        print(f'''El archivo '{filename}' YA EXISTE. Si guardas, PERDERÁS LA CLAVE ANTERIOR.''')
        
        # Pedir confirmación explícita para sobrescribir
        input_confirm = input("¿Deseas guardar la nueva clave y sobrescribir el archivo? (Escribe 'S' para sí): ")
        
        if input_confirm.upper() != 'S':
            print("[CANCELADO] El proceso ha sido detenido. No se ha guardado ninguna clave.")
            return # Detener la ejecución de forma segura

    KeyPersistence.save_key_to_file(private_key, filename)
    
    print(f'\nClave privada guardada en: tools/{filename}')
    print('\t-> Recuerda, ahora esta es tu nueva identidad.')

if __name__ == '__main__':
    main()