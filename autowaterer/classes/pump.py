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

    # Gets and sets the rate of the pump in ml/s
    def get_rate(self):
        return self.rate

    def set_rate(self, rate):
        self.rate = rate

    def get_time_elapsed(self):
        if self.start_time is None:
            return 0.0
        if self.is_running():
            return round(time.time() - self.start_time, 2)
        if self.end_time is None:
            return 0.0
        return round(self.end_time - self.start_time, 2)

    # Gets the pump status
    def is_running(self):
        return self.lock.locked()

    # These methods are just wrappers around the Relay class's on and off methods.
    def turn_on(self):
        if not self.lock.acquire(blocking=False):
            return False
        try:
            self.on()
            self.start_time = time.time()
            self.end_time = None
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
            print(f'Pump turned off after {self.get_time_elapsed()} seconds')
            return True
        except Exception as e:
            print(f'Error turning off pump: {e}')
            return False

    # Runs the water pump for a given quantity in ml
    def run_water_pump(self, quantity = 10):
        self.turn_on()
        time.sleep(quantity / self.rate)
        self.turn_off()
