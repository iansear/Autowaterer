from .relay import Relay
import threading
import time

class Pump(Relay):
    start_time = None
    end_time = None
    
    def __init__(self, gpio_pin, rate=1.25):
        super().__init__(gpio_pin, active_high=False)
        self.lock = threading.Lock()
        self.rate = rate

    # These methods are just wrappers around the Relay class's on and off methods.
    def turn_on(self):
        if not self.lock.acquire(blocking=False):
            return False
        try:
            self.on()
            self.start_time = time.time()
            return True
        except Exception as e:
            print(f'Error turning on pump: {e}')
            self.lock.release()
            return False

    def turn_off(self):
        try:
            self.off()
            self.end_time = time.time()
            self.lock.release()
            return True
        except Exception as e:
            print(f'Error turning off pump: {e}')
            return False

    # Gets the pump status
    def is_running(self):
        return self.lock.locked()

    # Sets and gets the rate of the pump in ml/s
    def set_rate(self, rate):
        self.rate = rate

    def get_rate(self):
        return self.rate

    # Test water pump for 10 seconds
    # def test_water_pump(self):
    #     self.turn_on()
    #     time.sleep(10)
    #     self.turn_off()

    def run_water_pump(self, quantity: float):
        self.turn_on()
        time.sleep(quantity / self.rate)
        self.turn_off()