# clients/esp32_sensor/physical_device/sensors_config.py

# Lista de configuración de sensores.
# Esto demuestra que la lógica de la red está desacoplada del hardware.
SENSORS_LIST = [
    # 1. Sensor Simulado (Funciona siempre, ideal para pruebas de red)
    {
        "id": "temp_dht_1",
        "type": "SIMULATED", 
        "pin": 15,           
        "interval": 5        
    },

    # 2. Otro Sensor Simulado para generar más tráfico
    {
        "id": "luz_analog_1",
        "type": "SIMULATED", 
        "pin": 34,           
        "interval": 2        
    },

    # 3. CASO: SENSOR FALTANTE O DESACTIVADO
    # El sistema ignorará este sensor, demostrando manejo de errores de configuración.
    {
        "id": "sensor_gas_futuro",
        "type": "DISABLED",  
        "pin": 0,            
        "interval": 60       
    }
]