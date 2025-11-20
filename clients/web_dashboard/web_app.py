# clients/web_dashboard/web_app.py
'''
class WebClient(BaseClient):
    Implementación concreta de un cliente Web/Humano.
    Hereda de BaseClient para la seguridad, pero implementa una interfaz 
    interactiva (CLI) para recibir input del usuario en tiempo real.

    Attributes:
        (Heredados de BaseClient): _builder, _gateway_url.

    Methods:
        run_interactive_chat(): Inicia el bucle de entrada de usuario.
            1. Solicitar entrada de texto por consola (input).
            2. Validar comandos de salida ('exit').
            3. Enviar mensaje usando el método del padre (send_data).
'''

import sys
import os
import logging

# Configuración de Imports (Añadir raíz del proyecto al path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from clients.base_client import BaseClient

class WebClient(BaseClient):
    
    def run_interactive_chat(self):
        print(f"\n=== WEB CHAT BLOCKCHAIN (ID: {self.get_my_address()}) ===")
        print("Escribe un mensaje y presiona ENTER. Escribe 'exit' para salir.\n")

        while True:
            try:
                # 1. Solicitar entrada de texto al usuario (Simulación de formulario HTML).
                msg = input("Mensaje > ")
                
                # 2. Validar comandos de salida o entradas vacías.
                if msg.lower() in ['exit', 'salir']: 
                    logging.info("Cerrando sesión de usuario...")
                    break
                if not msg.strip(): 
                    continue

                # 3. Enviar mensaje usando la lógica segura del padre.
                self.send_data(
                    data_type="USER_CHAT", 
                    content_str=msg, 
                    metadata={"app": "WebClient v1.0", "priority": "high"}
                )
                
            except KeyboardInterrupt:
                logging.info("Interrupción de usuario.")
                break
            except Exception as e:
                logging.error(f"Error en interfaz: {e}")

if __name__ == "__main__":
    # Inicializar el cliente con la identidad del usuario
    client = WebClient(key_file="user_key.pem")
    client.run_interactive_chat()