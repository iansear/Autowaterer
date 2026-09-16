from gpiozero import DistanceSensor
from time import sleep

# partial=True so a missing echo does not hang on queue.full.wait()
sensor = DistanceSensor(echo=17, trigger=4, max_distance=2, queue_len=5, partial=True)

try:
    while True:
        distance_m = sensor.distance
        if distance_m is None:
            print('Water level: no echo (check wiring, 5V echo divider, and that trigger/echo are not swapped)')
        else:
            print(f'Water level: {distance_m * 100:.2f} cm')
        sleep(1)

except KeyboardInterrupt:
    print('Keyboard interrupt')
finally:
    sensor.close()
    print('Sensor closed')
