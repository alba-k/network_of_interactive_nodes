# clients/esp32_sensor/physical_device/boot.py
import network
import time
import machine
import config

class WiFiManager:
    def __init__(self):
        self._led = machine.Pin(2, machine.Pin.OUT)
        self._wlan = network.WLAN(network.STA_IF)

    def connect(self):
        self._wlan.active(True)
        if self._wlan.isconnected():
            print("✅ WiFi activo:", self._wlan.ifconfig()[0])
            return True

        print("📡 Conectando a {}...".format(config.WIFI_SSID))
        self._wlan.connect(config.WIFI_SSID, config.WIFI_PASS)

        start = time.time()
        while not self._wlan.isconnected():
            self._led.value(not self._led.value())
            time.sleep(0.5)
            if time.time() - start > config.WIFI_TIMEOUT:
                print("❌ Timeout WiFi")
                self._led.value(0)
                return False

        self._led.value(1)
        print("✅ Conectado IP:", self._wlan.ifconfig()[0])
        return True

manager = WiFiManager()
manager.connect()