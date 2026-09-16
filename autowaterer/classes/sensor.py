from gpiozero import DistanceSensor

class Sensor(DistanceSensor):
    def __init__(self, echo, trigger):
        super().__init__(echo, trigger)

    def get_distance(self):
        return self.distance