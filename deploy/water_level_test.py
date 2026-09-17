from gpiozero import DistanceSensor
from time import sleep

# partial=True so a missing echo does not hang on queue.full.wait()
sensor = DistanceSensor(echo=17, trigger=4)#, max_distance=2, queue_len=5, partial=True)

try:
    while True:
        distance_m = sensor.distance
        if distance_m is None:
            print('Water level: no echo (check wiring, 5V echo divider, and that trigger/echo are not swapped)')
        else:
            distance_cm = distance_m * 100
            print(f'Water level: {distance_cm:.2f} cm')
            difference = 31 - distance_cm
            print(f'Difference: {difference:.2f} cm')
            percentage = round((difference / 31) * 100, 1)
            print(f'Percentage: {percentage:.2f}%')
        sleep(1)

except KeyboardInterrupt:
    print('Keyboard interrupt')
finally:
    sensor.close()
    print('Sensor closed')

# 31 is empty
# 28 is low