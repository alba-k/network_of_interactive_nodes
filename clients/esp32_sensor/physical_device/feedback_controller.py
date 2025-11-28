# clients/esp32_sensor/physical_device/feedback_controller.py
import machine
import time

class FeedbackController:
    """
    [POO: ABSTRACCIÓN Y ENCAPSULAMIENTO]
    Aísla la interacción con el GPIO (Pin 2) del resto de la lógica. 
    El 'main' no sabe cómo parpadea, solo llama al método.
    """
    def __init__(self, pin_number=2):
        self._led = machine.Pin(pin_number, machine.Pin.OUT)
        self.reset()

    def reset(self):
        self._led.value(0)

    def indicate_success(self):
        """Patrón de luz para indicar que la TX fue aceptada por el Gateway (200 OK)."""
        self._led.value(1)
        time.sleep(0.5)
        self._led.value(0)

    def indicate_error(self):
        """Patrón de luz para indicar ERROR (Timeout, No encontrado, Conexión abortada)."""
        for _ in range(3):
            self._led.value(1)
            time.sleep(0.1)
            self._led.value(0)
            time.sleep(0.1)