import threading
from autowaterer.classes.sensor import Sensor

water_sensor = None

def init_water_sensor():
    global water_sensor
    water_sensor = Sensor(echo=17, trigger=4)
    return water_sensor

def get_water_sensor():
    return water_sensor

def close_water_sensor():
    global water_sensor
    if water_sensor is None:
        return
    sensor = water_sensor
    water_sensor = None
    # gpiozero DistanceSensor.close() can block forever waiting for an echo
    # pulse, which is what hangs Ctrl+C. Do not wait more than a moment.
    closer = threading.Thread(target=_close_sensor, args=(sensor,), daemon=True)
    closer.start()
    closer.join(timeout=0.5)

def _close_sensor(sensor):
    try:
        sensor.close()
    except Exception as e:
        print(f'Error closing water sensor: {e}')
