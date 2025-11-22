import os

# --- CONFIGURACIÓN ---
IGNORAR_CARPETAS = {'__pycache__', '.git', '.vscode', 'venv', 'env', '.idea', 'node_modules'}
EXTENSION_CODE = '.py'

def imprimir_codigo_de_ruta(ruta_objetivo):
    print(f"\n{'='*50}")
    print(f"🖨️  IMPRIMIENDO ARCHIVOS .PY EN: {ruta_objetivo}")
    print(f"{'='*50}\n")
    
    nombre_script = os.path.basename(__file__)
    archivos_encontrados = False

    # Recorremos la carpeta elegida (y sus subcarpetas si las hubiera)
    for raiz, dirs, archivos in os.walk(ruta_objetivo):
        # Limpiar carpetas basura
        dirs[:] = [d for d in dirs if d not in IGNORAR_CARPETAS]

        for archivo in archivos:
            if archivo.endswith(EXTENSION_CODE) and archivo != nombre_script:
                archivos_encontrados = True
                ruta_completa = os.path.join(raiz, archivo)
                
                try:
                    with open(ruta_completa, 'r', encoding='utf-8') as f:
                        contenido = f.read()
                        print(f"Archivo: {ruta_completa}")
                        print("```python")
                        print(contenido)
                        print("```")
                        print("\n")
                except Exception as e:
                    print(f"[Error leyendo {archivo}: {e}]")
    
    if not archivos_encontrados:
        print("⚠️  No encontré archivos .py en esta carpeta.")

def iniciar_navegacion():
    ruta_actual = '.'
    
    while True:
        # 1. Escanear el directorio actual
        try:
            elementos = os.listdir(ruta_actual)
        except Exception as e:
            print(f"Error accediendo a {ruta_actual}: {e}")
            break

        # Separar carpetas y archivos py
        carpetas = []
        archivos_py = []
        
        for item in elementos:
            ruta_item = os.path.join(ruta_actual, item)
            if os.path.isdir(ruta_item):
                if item not in IGNORAR_CARPETAS:
                    carpetas.append(item)
            elif item.endswith(EXTENSION_CODE):
                archivos_py.append(item)
        
        carpetas.sort()

        # 2. Mostrar interfaz
        print(f"\n📂 ESTÁS EN: {os.path.abspath(ruta_actual)}")
        if archivos_py:
            print(f"   📄 (Hay {len(archivos_py)} archivos Python aquí)")
        else:
            print("   (No hay archivos .py sueltos aquí, solo carpetas)")

        print("\n--- ELIGE UNA OPCIÓN ---")
        
        # Listar carpetas para entrar
        for i, carpeta in enumerate(carpetas):
            print(f"[{i+1}] 📁 Entrar a '{carpeta}'")
        
        print("-" * 30)
        print(f"[P] 🖨️  IMPRIMIR TODO el código en esta carpeta")
        
        if ruta_actual != '.':
            print(f"[A] ⬅️  Atrás (Subir un nivel)")
        
        print(f"[S] ❌ Salir")

        # 3. Capturar decisión
        eleccion = input("\nTu elección: ").upper().strip()

        if eleccion == 'S':
            print("Saliendo...")
            break
        
        elif eleccion == 'A' and ruta_actual != '.':
            # Subir un nivel
            ruta_actual = os.path.dirname(ruta_actual)
            # Si subimos hasta vacío, volver a '.'
            if not ruta_actual: ruta_actual = '.'
            
        elif eleccion == 'P':
            # Acción final: Imprimir
            imprimir_codigo_de_ruta(ruta_actual)
            break # Terminamos después de imprimir
            
        elif eleccion.isdigit():
            indice = int(eleccion) - 1
            if 0 <= indice < len(carpetas):
                # Entrar a la carpeta seleccionada
                nueva_carpeta = carpetas[indice]
                ruta_actual = os.path.join(ruta_actual, nueva_carpeta)
            else:
                print("\n⚠️  Número inválido, intenta de nuevo.")
        else:
            print("\n⚠️  Opción no reconocida.")

if __name__ == "__main__":
    iniciar_navegacion()