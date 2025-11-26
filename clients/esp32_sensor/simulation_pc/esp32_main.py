# clients/esp32_sensor/esp32_main.py
'''
class ESP32Client(BaseClient):
    Hereda de BaseClient para obtener la capacidad de firmar y enviar datos, y añade un bucle infinito que simula la lectura de sensores físicos.

    Attributes:
        (Heredados de BaseClient): _builder, _gateway_url.

    Methods:
        run_sensor_loop(): Ejecuta el ciclo de vida del dispositivo (Leer -> Enviar -> Dormir).
            1. Generar datos aleatorios (Simulación de Hardware).
            2. Construir el payload de texto.
            3. Enviar datos usando el método del padre (send_data).
            4. Dormir (Simulación de eficiencia energética).
'''

import time
import random
import sys
import os
import logging

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Importación del Cliente Base
from clients.base_client import BaseClient

class ESP32Client(BaseClient):

    # Configuración del dispositivo
    DEVICE_ID: str = "ESP32-Sim-01"
    LOCATION: str = "Warehouse-A"
    SLEEP_INTERVAL_SEC: int = 5

    def run_sensor_loop(self) -> None:
        logging.info(f">>> SENSOR IOT ACTIVO ({self.DEVICE_ID}) <<<")
        logging.info(f"Conectado a Gateway: {self._gateway_url}")
        
        while True:
            try:
                temp: float = round(random.uniform(20.0, 35.0), 2)
                hum: float = round(random.uniform(40.0, 80.0), 2)
                
                # 2. Construir el payload de texto (Formato del protocolo IoT).
                payload: str = f"T:{temp}|H:{hum}"
                logging.info(f"Lectura Sensor: {payload}")

                # 3. Enviar datos usando el método heredado (Abstracción de firma/red).
                # BaseClient se encarga de usar TransactionBuilder y firmar criptográficamente.
                success: bool = self.send_data(
                    data_type="IOT_METRICS", 
                    content_str=payload, 
                    metadata={"device": self.DEVICE_ID, "location": self.LOCATION}
                )
                
                if success:
                    logging.info("✅ Dato confirmado por el Gateway.")
                else:
                    logging.warning("❌ El Gateway rechazó el dato.")

            except ConnectionError:
                logging.error("Fallo de Red: No se puede conectar al Gateway. Reintentando...")
            except Exception as e:
                logging.error(f"Fallo crítico en ciclo de sensor: {e}")

            # 4. Dormir (Simulación de Deep Sleep para ahorro de batería).
            time.sleep(self.SLEEP_INTERVAL_SEC)

if __name__ == "__main__":
    # Configuración de Logging para el Cliente
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s [%(levelname)s] CLIENT: %(message)s',
        datefmt='%H:%M:%S'
    )

    # Configuración de rutas
    # Buscamos la clave en la misma carpeta que este script
    key_file_path = os.path.join(current_dir, "sensor_key.pem")
    
    # URL del Gateway (Debe coincidir con donde corre el GatewayNode)
    # Si GatewayNode está en puerto P2P 8001, su API suele estar en 8002.
    # Si usaste los defaults (Gateway en 8000), la API suele estar en 8000.
    # Ajusta esto según cómo lances main.py.
    GATEWAY_API_URL = "http://127.0.0.1:8000" 

    try:
        # Inicializar el cliente con su identidad única y destino
        client = ESP32Client(
            key_file=key_file_path, 
            gateway_url=GATEWAY_API_URL
        )
        client.run_sensor_loop()
        
    except KeyboardInterrupt:
        logging.info("Sensor detenido por usuario.")
    except Exception as e:
        logging.critical(f"No se pudo iniciar el sensor: {e}")
        logging.info("Tip: Asegúrate de generar 'sensor_key.pem' primero.")