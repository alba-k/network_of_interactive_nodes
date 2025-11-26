# clients/esp32_sensor/physical_device/sensors_config.py

# Lista de configuración de sensores.
# ID: Nombre único para identificar el dato.
# TYPE: 
#    - "DHT22" / "DHT11": Sensores reales.
#    - "ANALOG": Sensor analógico real.
#    - "SIMULATED": Genera datos falsos (útil si no tienes el sensor físico pero quieres probar la red).
#    - "DISABLED": Úsalo para sensores desconectados o faltantes (el sistema los ignorará).

SENSORS_LIST = [
    # 1. Sensor Simulado (Funciona siempre, ideal para pruebas)
    {
        "id": "temp_dht_1",
        "type": "SIMULATED", 
        "pin": 15,           
        "interval": 5        
    },

    # 2. Otro Sensor Simulado
    {
        "id": "luz_analog_1",
        "type": "SIMULATED", 
        "pin": 34,           
        "interval": 2        
    },

    # 3. CASO: SENSOR FALTANTE O DESACTIVADO
    # Si tienes un sensor planeado pero no instalado, configúralo como "DISABLED"
    # El sistema verá que el tipo no es válido y no intentará leerlo ni enviará datos.
    {
        "id": "sensor_gas_futuro",
        "type": "DISABLED",  # <--- ESTO EVITA QUE SE LEA
        "pin": 0,            # El pin no importa
        "interval": 60       # El intervalo no importa
    }
]