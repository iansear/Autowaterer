from autowaterer.classes.pump import Pump

water_pump_1 = None

def init_pump_1():
    global water_pump_1
    if water_pump_1 is None:
        water_pump_1 = Pump(12, 1.25)
        print('Water pump 1 initialized...')
    else:
        print('Water pump 1 already initialized...')
