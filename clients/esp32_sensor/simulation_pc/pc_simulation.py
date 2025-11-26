# clients/esp32_sensor/simulation_pc/pc_simulation.py
'''
Script de Simulación para PC.
Usa la librería criptográfica completa del proyecto (Core) para firmar transacciones localmente.
NO apto para subir al chip ESP32 (usa demasiada RAM/Librerías).
'''

import time
import random
import sys
import os
import logging

# --- [MODIFICACIÓN CLAVE] AJUSTE DE RUTAS ---
# Como movimos este archivo una carpeta más adentro (simulation_pc),
# necesitamos subir 3 niveles (../../../) para encontrar la raíz del proyecto.
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../../../')) 

# Verificación de seguridad para imports
if project_root not in sys.path:
    sys.path.append(project_root)

# Ahora sí podemos importar el Cliente Base del proyecto
try:
    from clients.base_client import BaseClient
except ImportError as e:
    print(f"❌ Error de Importación: {e}")
    print(f"   Ruta intentada: {project_root}")
    print("   Verifica que la estructura de carpetas sea correcta.")
    sys.exit(1)

class ESP32Simulation(BaseClient):

    # Configuración de este "Dispositivo Virtual"
    DEVICE_ID: str = "PC-Simulated-Node"
    LOCATION: str = "Debug-Station-01"
    SLEEP_INTERVAL_SEC: int = 5

    def run_sensor_loop(self) -> None:
        logging.info(f">>> SIMULADOR PC INICIADO ({self.DEVICE_ID}) <<<")
        logging.info(f"Conectado a Gateway: {self._gateway_url}")
        
        while True:
            try:
                # 1. Simular datos (Hardware Virtual)
                temp: float = round(random.uniform(20.0, 35.0), 2)
                hum: float = round(random.uniform(40.0, 80.0), 2)
                
                # 2. Construir payload
                payload: str = f"T:{temp}|H:{hum}"
                logging.info(f"Generando dato: {payload}")

                # 3. Enviar (BaseClient firma automáticamente usando la PEM local)
                #    A diferencia del ESP32 real, aquí la PC tiene potencia para firmar.
                success: bool = self.send_data(
                    data_type="IOT_METRICS", 
                    content_str=payload, 
                    metadata={
                        "device": self.DEVICE_ID, 
                        "location": self.LOCATION,
                        "mode": "SIMULATION_FULL_CRYPTO"
                    }
                )
                
                if success:
                    logging.info("✅ Transacción confirmada por Gateway.")
                else:
                    logging.warning("❌ Gateway rechazó la transacción.")

            except ConnectionError:
                logging.error("Fallo de conexión HTTP. ¿El Gateway está corriendo?")
            except Exception as e:
                logging.error(f"Error en bucle: {e}")

            time.sleep(self.SLEEP_INTERVAL_SEC)

if __name__ == "__main__":
    # Configuración de Logging
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s [%(levelname)s] SIM: %(message)s',
        datefmt='%H:%M:%S'
    )

    # --- [MODIFICACIÓN] BÚSQUEDA DE LLAVE ---
    # Busca la llave en ESTA carpeta (simulation_pc)
    key_file_path = os.path.join(current_dir, "sensor_key.pem")
    
    # URL del Gateway (API)
    GATEWAY_API_URL = "http://127.0.0.1:8000" 

    if not os.path.exists(key_file_path):
        logging.critical(f"⛔ FALTA LA LLAVE: No se encontró 'sensor_key.pem' en {current_dir}")
        logging.info("   -> Por favor copia tu archivo .pem a esta carpeta.")
        sys.exit(1)

    try:
        client = ESP32Simulation(
            key_file=key_file_path, 
            gateway_url=GATEWAY_API_URL
        )
        client.run_sensor_loop()
        
    except KeyboardInterrupt:
        logging.info("Simulación detenida.")