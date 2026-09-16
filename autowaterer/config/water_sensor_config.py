from autowaterer.classes.sensor import Sensor

water_sensor = None

def init_water_sensor():
    global water_sensor
    water_sensor = Sensor(echo=17, trigger=4)