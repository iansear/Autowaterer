from gpiozero import DistanceSensor
from time import sleep

sensor = DistanceSensor(echo=17, trigger=4)

while True:
    distance = sensor.distance * 100
    print(f'Water level: {distance:.2f} cm')
    sleep(1)