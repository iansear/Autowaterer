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
    try:
        water_sensor.close()
    except Exception as e:
        print(f'Error closing water sensor: {e}')
    water_sensor = None
