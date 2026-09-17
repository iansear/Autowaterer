import threading

loaded_water_level_sensors = {}

def stop_all_water_level_sensors():
    for sensor in list(loaded_water_level_sensors.values()):
        closer = threading.Thread(target=_close_sensor, args=(sensor,), daemon=True)
        closer.start()
        closer.join(timeout=0.5)

def _close_sensor(sensor):
    try:
        sensor.close()
    except Exception as e:
        print(f'Error closing water level sensor: {e}')
