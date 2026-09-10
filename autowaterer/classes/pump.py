from datetime import datetime
from .relay import Relay
import threading
import time

class Pump(Relay):
    def __init__(self, gpio_pin, rate=1.25):
        super().__init__(gpio_pin, active_high=False)
        self.lock = threading.Lock()
        self.rate = rate
        self.start_time = None
        self.end_time = None
        self.last_run = None
        self._stop = threading.Event()

    def interrupt(self):
        """Wake a timed run so shutdown does not wait on sleep."""
        self._stop.set()

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

    def get_last_run(self):
        return self.last_run

    def is_running(self):
        return self.lock.locked()

    def turn_on(self):
        if not self.lock.acquire(blocking=False):
            return False
        try:
            self._stop.clear()
            self.on()
            self.start_time = time.time()
            self.end_time = None
            self.last_run = datetime.now()
            return True
        except Exception as e:
            print(f'Error turning on pump: {e}')
            self.lock.release()
            return False

    def turn_off(self):
        try:
            self.off()
            self.end_time = time.time()
            print(f'Pump turned off after {self.get_time_elapsed()} seconds')
            return True
        except Exception as e:
            print(f'Error turning off pump: {e}')
            return False
        finally:
            if self.lock.locked():
                try:
                    self.lock.release()
                except RuntimeError:
                    pass

    def run_water_pump(self, quantity=10):
        if not self.turn_on():
            return False
        try:
            duration = max(float(quantity) / self.rate, 0)
            deadline = time.monotonic() + duration
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                if self._stop.wait(timeout=min(0.2, remaining)):
                    break
        finally:
            self.turn_off()
        return True
