import spidev
from time import sleep

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000

def read_channel(channel):
    adc = spi.xfer2([1, (8 + channel) << 4, 0])
    data = ((adc[1] & 3) << 8) | adc[2]
    return data

try:
    while True:
        sensor_value = read_channel(0)
        print(f'Sensor value: {sensor_value}')
        sleep(1)
except KeyboardInterrupt:
    print('Keyboard interrupt')
finally:
    spi.close()
    print('SPI closed')
