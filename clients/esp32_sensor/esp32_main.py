# clients/esp32_sensor/esp32_main.py
'''
class ESP32Client(BaseClient):
    Implementación concreta de un cliente IoT (Simulado). 
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

# 1. Configuración de Imports (Añadir raíz del proyecto al path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from clients.base_client import BaseClient

class ESP32Client(BaseClient):

    def run_sensor_loop(self):
        logging.info(">>> SENSOR IOT ACTIVO (Bucle Infinito) <<<")
        
        while True:
            try:
                # 1. Generar datos aleatorios (Simulación de lectura de pines GPIO).
                temp = round(random.uniform(20.0, 35.0), 2)
                hum = round(random.uniform(40.0, 80.0), 2)
                
                # 2. Construir el payload de texto (Formato del protocolo IoT).
                payload = f"T:{temp}|H:{hum}"
                logging.info(f"Lectura Sensor: {payload}")

                # 3. Enviar datos usando el método heredado (Abstracción de firma/red).
                success = self.send_data(
                    data_type="IOT_METRICS", 
                    content_str=payload, 
                    metadata={"device": "ESP32-Sim", "location": "Warehouse-A"}
                )
                
                if success:
                    logging.info("Dato confirmado por el Gateway.")

            except Exception as e:
                logging.error(f"Fallo en ciclo de sensor: {e}")

            # 4. Dormir (Simulación de Deep Sleep para ahorro de batería).
            time.sleep(5)

if __name__ == "__main__":
    # Inicializar el cliente con su identidad única
    client = ESP32Client(key_file="sensor_key.pem")
    client.run_sensor_loop()