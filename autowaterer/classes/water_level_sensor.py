from gpiozero import DistanceSensor

class WaterLevelSensor(DistanceSensor):
    def __init__(self, echo, trigger):
        super().__init__(echo=echo, trigger=trigger)

    def get_distance(self):
        distance_m = self.distance
        if distance_m is None:
            return None
        return round(distance_m * 100, 1)
