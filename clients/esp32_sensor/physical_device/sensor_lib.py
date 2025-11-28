# clients/esp32_sensor/physical_device/sensor_lib.py

from machine import Pin, ADC
import dht
import random

class SensorFactory:
    """
    [PATRÓN DE DISEÑO: FACTORY]
    Encapsula la lógica de creación de objetos Sensor.
    Cumple el principio Open/Closed: Puedes agregar nuevos tipos de sensores (Ultrasonic, BME680)
    simplemente añadiendo una nueva condición 'elif' y la clase Wrapper correspondiente.
    """
    @staticmethod
    def create_sensor(config):
        s_type = config.get('type')
        pin = config.get('pin', 0)
        
        if s_type == 'DHT22':
            return DHTSensorWrapper(pin, 'DHT22')
        elif s_type == "DHT11":
            return DHTSensorWrapper(pin, 'DHT11')
        elif s_type == 'ANALOG':
            return AnalogSensorWrapper(pin)
        elif s_type == 'SIMULATED':
            # La opción que usamos en la defensa
            return SimulatedSensor()
        elif s_type == 'DISABLED':
            return None # <--- Aquí se descarta el sensor desactivado
        else:
            print("⚠️ Tipo desconocido:", s_type)
            return None

# --- Clases Wrappers ---

class DHTSensorWrapper:
    def __init__(self, pin_num, model):
        try:
            self._dht = dht.DHT22(Pin(pin_num)) if model == "DHT22" else dht.DHT11(Pin(pin_num))
            self.type = "ENV_METRICS"
        except Exception:
            self._dht = None

    def read(self):
        if not self._dht: return None
        try:
            self._dht.measure()
            return "T:{}|H:{}".format(self._dht.temperature(), self._dht.humidity())
        except OSError:
            return None 

class AnalogSensorWrapper:
    def __init__(self, pin_num):
        self._adc = ADC(Pin(pin_num))
        self._adc.atten(ADC.ATTN_11DB)
        self.type = "ANALOG_VAL"

    def read(self):
        return str(self._adc.read())

class SimulatedSensor:
    def __init__(self):
        self.type = "SIM_DATA"

    def read(self):
        # Genera datos simulados (la funcionalidad que usaste en la defensa)
        return str(round(random.uniform(20.0, 45.0), 2))