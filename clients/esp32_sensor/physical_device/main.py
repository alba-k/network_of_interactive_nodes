# clients/esp32_sensor/physical_device/main.py (VERSIÓN FINAL CON LEDS Y POO)
import time
import urequests as requests
import ubinascii
import config
import sensors_config
from sensor_lib import SensorFactory
# [NUEVA IMPORTACIÓN] Traemos la clase que maneja las luces (POO)
from feedback_controller import FeedbackController 

# 1. Instancia del controlador de luces
feedback = FeedbackController() 

# 2. Cargar solo sensores válidos
active_sensors = []
print("\n>>> INICIANDO SISTEMA ESP32 <<<")

for conf in sensors_config.SENSORS_LIST:
    obj = SensorFactory.create_sensor(conf)
    if obj: # Si el tipo de sensor es válido
        active_sensors.append({
            "obj": obj,
            "id": conf["id"],
            "last_read": 0,
            "interval": conf.get("interval", 5)
        })
        print(" + Cargado:", conf["id"])
    else:
        print(" - Ignorado (Desactivado/Invalido):", conf["id"])


def run():
    print(">>> Destino:", config.GATEWAY_URL)
    # Apagamos luz al inicio para diferenciar del boot.py
    feedback.reset() 
    
    while True:
        now = time.time()
        
        for sensor in active_sensors:
            if now - sensor["last_read"] >= sensor["interval"]:
                try:
                    raw_val = sensor["obj"].read()
                    if raw_val is None: continue

                    # Codificación y Preparación de Payload
                    val_b64 = ubinascii.b2a_base64(raw_val.encode('utf-8')).decode('utf-8').strip()
                    uid = "{}_{}".format(config.DEVICE_ID, sensor["id"])
                    
                    payload = {
                        "source_id": uid,
                        "data_type": sensor["obj"].type,
                        "value": val_b64,
                        "nonce": int(now),
                        "metadata": {"sensor": sensor["id"], "hw": config.DEVICE_ID}
                    }

                    print("📡 Enviando datos...", end="")
                    # 3. Enviar al Servidor
                    res = requests.post("{}/submit_data".format(config.GATEWAY_URL), json=payload)
                    
                    if res.status_code == 200:
                        print(" ✅ OK")
                        # [DELEGACIÓN POO] Llama al controlador para el Feedback Físico
                        feedback.indicate_success() 
                        sensor["last_read"] = now
                    else:
                        print(" ❌ Error", res.status_code)
                        # [DELEGACIÓN POO] Llama al patrón de error
                        feedback.indicate_error() 
                    res.close()

                except Exception as e:
                    print("\n⚠️ Error:", e)
                    # Llama al patrón de error si hay un fallo de red
                    feedback.indicate_error() 

        time.sleep(1)

if __name__ == '__main__':
    run()