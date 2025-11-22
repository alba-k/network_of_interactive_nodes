# tools/wallet_cli.py
'''
Script Interactivo para gestión de Billeteras BIP-39.
Permite al usuario:
1. Crear una nueva identidad (ver las 12 palabras).
2. Recuperar una identidad existente (ingresar las 12 palabras).
3. Guardar el resultado en un archivo .pem listo para usar por el Nodo.
'''

import sys
import os

# Ajuste de path para importar 'identity'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from identity.mnemonic_service import MnemonicService

def main():
    print("="*60)
    print("  GESTOR DE BILLETERAS BIP-39 (BLOCKCHAIN EDUCATIVA)")
    print("="*60)
    print("1. Crear NUEVA Billetera (Generar palabras)")
    print("2. RECUPERAR Billetera (Tengo mis palabras)")
    print("="*60)
    
    opcion = input("Seleccione una opción [1/2]: ").strip()
    
    mnemonic_phrase = ""
    
    if opcion == "1":
        print("\n>>> GENERANDO NUEVA IDENTIDAD...")
        mnemonic_phrase = MnemonicService.generate_new_mnemonic()
        print("\n" + "!"*60)
        print("IMPORTANTE: Anote estas 12 palabras en papel y guárdelas en un lugar seguro.")
        print("Si las pierde, perderá sus fondos para siempre.")
        print("!"*60)
        print(f"\nFRASE SEMILLA:\n\n{mnemonic_phrase}\n")
        input("Presione ENTER cuando las haya anotado...")
        
    elif opcion == "2":
        print("\n>>> RECUPERACIÓN DE IDENTIDAD...")
        print("Ingrese sus 12 palabras separadas por espacios:")
        mnemonic_phrase = input("> ").strip()
    
    else:
        print("Opción inválida.")
        return

    # --- Generación del Archivo .pem ---
    try:
        print("\n... Derivando claves criptográficas ...")
        # 1. Convertir palabras a Clave Privada ECC
        private_key = MnemonicService.mnemonic_to_private_key(mnemonic_phrase)
        
        # 2. Obtener nombre de archivo
        filename = input("\nNombre del archivo a guardar (ej. wallet_8000.pem): ").strip()
        if not filename: filename = "wallet.pem"
        
        # 3. Exportar a formato PEM
        with open(filename, "wt") as f:
            f.write(private_key.export_key(format='PEM'))
            
        print(f"\n✅ ÉXITO: Billetera guardada en '{filename}'")
        print(f"🔑 Clave Pública (Address): (Generada al arrancar el nodo)")
        
        # Validación extra: Mostrar las palabras usadas para confirmar
        if opcion == "2":
            print("(Identidad restaurada correctamente)")

    except ValueError as e:
        print(f"\n❌ ERROR: {e}")
    except Exception as e:
        print(f"\n❌ ERROR INESPERADO: {e}")

if __name__ == "__main__":
    main()