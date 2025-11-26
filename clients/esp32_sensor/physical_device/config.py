# network_of_interactive_nodes/clients/esp32_sensor/physical_device/config.py
# Sube este archivo al ESP32.

# CREDENCIALES WIFI
WIFI_SSID = 'FLIA. VACA'
WIFI_PASS = '211064831'
WIFI_TIMEOUT = 15  # Segundos máximos para intentar conectar

# CONFIGURACIÓN DE RED (GATEWAY)
GATEWAY_IP = '192.168.0.7' 
GATEWAY_PORT = 8001  # Puerto de la API
GATEWAY_URL = 'http://{}:{}'.format(GATEWAY_IP, GATEWAY_PORT)

# IDENTIDAD DEL DISPOSITIVO
DEVICE_ID = '1EdZafU1YxXA8KnaMxLppvzxYQc83ZJvGf'

# COMPORTAMIENTO
LOOP_DELAY_SECONDS = 0.1  # Pausa técnica para no saturar la CPU