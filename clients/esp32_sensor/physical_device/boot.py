# clients/esp32_sensor/physical_device/boot.py (VERSION FINAL Y ROBUSTA)
import network
import time
import machine
import config

def connect():
    led = machine.Pin(2, machine.Pin.OUT)
    led.value(1) 
    
    wlan = network.WLAN(network.STA_IF)
    
    # [ROBUSTEZ] Forzar reinicio del radio para evitar el error 'Wifi Internal Error'
    wlan.active(False) 
    time.sleep(1)
    wlan.active(True)
    
    print('📡 Conectando a:', config.WIFI_SSID)
    
    try:
        wlan.connect(config.WIFI_SSID, config.WIFI_PASS)
    except Exception:
        # Se ignora la excepción, el bucle de abajo la manejará
        pass

    # [MANEJO DE ERRORES] Bucle con Límite de Tiempo (Timeout)
    intentos = 0
    while not wlan.isconnected() and intentos < 20: 
        led.value(not led.value())
        time.sleep(0.5)
        intentos += 1
        print(".", end="")
            
    if wlan.isconnected():
        print('\n✅ Conectado IP:', wlan.ifconfig()[0])
        led.value(1)
    else:
        print('\n❌ TIMEOUT. No conectó. (Modo seguro)')
        led.value(0) 

connect()