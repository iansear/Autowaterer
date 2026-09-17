from gpiozero import DistanceSensor

class WaterLevelSensor(DistanceSensor):
    def __init__(self, echo, trigger, resevoir_depth=0, resevoir_height=10):
        super().__init__(echo=echo, trigger=trigger)
        self.resevoir_depth = resevoir_depth
        self.resevoir_height = resevoir_height

    def get_resevoir_depth(self):
        return self.resevoir_depth

    def set_resevoir_depth(self, depth):
        self.resevoir_depth = depth

    def get_resevoir_height(self):
        return self.resevoir_height

    def set_resevoir_height(self, height):
        self.resevoir_height = height

    def get_distance(self):
        if self.distance is None:
            return None
        return round(self.distance * 100, 1)

    def get_water_level(self):
        if self.get_distance() is None:
            return (None, None)
        difference = self.resevoir_depth - self.get_distance()
        percentage = round((difference / self.resevoir_depth) * 100, 1)
        return (percentage, difference)