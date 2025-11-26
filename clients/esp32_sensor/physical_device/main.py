# clients/esp32_sensor/physical_device/main.py
import time
import urequests as requests
import ubinascii
import config
import sensors_config
from sensor_lib import SensorFactory

# 1. Cargar solo sensores válidos
active_sensors = []
print("\n>>> INICIANDO SISTEMA ESP32 <<<")

for conf in sensors_config.SENSORS_LIST:
    obj = SensorFactory.create_sensor(conf)
    if obj: # Si no es None (es decir, no es DISABLED)
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
    
    while True:
        now = time.time()
        
        for sensor in active_sensors:
            if now - sensor["last_read"] >= sensor["interval"]:
                try:
                    raw_val = sensor["obj"].read()
                    if raw_val is None: continue

                    val_b64 = ubinascii.b2a_base64(raw_val.encode('utf-8')).decode('utf-8').strip()
                    uid = "{}_{}".format(config.DEVICE_ID, sensor["id"])
                    
                    payload = {
                        "source_id": uid,
                        "data_type": sensor["obj"].type,
                        "value": val_b64,
                        "nonce": int(now),
                        "metadata": {"sensor": sensor["id"], "hw": config.DEVICE_ID}
                    }

                    print("📡 {} -> ".format(sensor["id"]), end="")
                    res = requests.post("{}/submit_data".format(config.GATEWAY_URL), json=payload)
                    
                    if res.status_code == 200:
                        print("✅ OK")
                        sensor["last_read"] = now
                    else:
                        print("❌", res.status_code)
                    res.close()

                except Exception as e:
                    print("\n⚠️ Error:", e)

        time.sleep(config.LOOP_DELAY_SECONDS)

if __name__ == '__main__':
    run()