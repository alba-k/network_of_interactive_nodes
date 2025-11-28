import os
import shutil
import glob

def mostrar_menu():
    print("\n" + "="*50)
    print("🧹  HERRAMIENTA DE LIMPIEZA PROFUNDA")
    print("="*50)
    print("Este script eliminará archivos generados por la red.")
    print("Selecciona qué deseas borrar:\n")
    print("  [1] Solo Historial (Blockchain y Mempool) -> Mantiene tus claves.")
    print("  [2] TODO (Historial + Claves .pem)        -> Reinicio de fábrica total.")
    print("  [3] Cancelar")
    print("="*50)

def borrar_historial():
    patrones = ["data_node_*", "__pycache__"]
    encontrados = []
    
    for pat in patrones:
        encontrados.extend(glob.glob(pat))
    
    if not encontrados:
        print("✅ No hay historial que borrar.")
        return

    print(f"\n⚠️  Se borrarán {len(encontrados)} carpetas de datos.")
    confirm = input("¿Confirmar borrado de HISTORIAL? (s/n): ").lower()
    
    if confirm == 's':
        for item in encontrados:
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                print(f"🗑️  Eliminado: {item}")
            except Exception as e:
                print(f"❌ Error eliminando {item}: {e}")
        print("\n✨ Historial eliminado. La red empezará desde cero.")
    else:
        print("Operación cancelada.")

def borrar_todo():
    # Borra historial primero
    borrar_historial()
    
    # Ahora busca las claves
    claves = glob.glob("*.pem")
    
    if not claves:
        print("✅ No hay claves (.pem) que borrar.")
        return

    print(f"\n⚠️  ¡ATENCIÓN! Se encontraron {len(claves)} claves privadas:")
    for k in claves:
        print(f"   - 🔑 {k}")
        
    print("\nSi borras esto, perderás tus identidades y direcciones para siempre.")
    confirm = input("¿Estás 100% seguro de borrar las CLAVES? (escribe 'borrar'): ")
    
    if confirm == 'borrar':
        for k in claves:
            try:
                os.remove(k)
                print(f"🔥 Eliminada: {k}")
            except Exception as e:
                print(f"❌ Error: {e}")
        print("\n✨ Sistema completamente reseteado (Tabula Rasa).")
    else:
        print("Las claves NO se tocaron.")

if __name__ == "__main__":
    while True:
        mostrar_menu()
        opcion = input("\nTu elección: ")
        
        if opcion == '1':
            borrar_historial()
            break
        elif opcion == '2':
            borrar_todo()
            break
        elif opcion == '3':
            print("Saliendo...")
            break
        else:
            print("Opción inválida.")