from gpiozero import DistanceSensor

class WaterLevelSensor(DistanceSensor):
    def __init__(self, echo, trigger, id=None, name='Unknown', resevoir_depth=30):
        depth_m = max(float(resevoir_depth) / 100.0, 0.2)
        super().__init__(
            echo=echo,
            trigger=trigger,
            max_distance=depth_m + 0.3,
            queue_len=5,
            partial=True,
        )
        self.id = id
        self.name = name
        self.resevoir_depth = float(resevoir_depth)

    def get_resevoir_depth(self):
        return self.resevoir_depth

    def set_resevoir_depth(self, depth):
        self.resevoir_depth = float(depth)

    def get_distance_cm(self):
        distance_m = self.distance
        if distance_m is None:
            return None
        return round(distance_m * 100, 1)

    def get_water_level_percentage(self):
        height = self.get_water_level_difference_cm()
        if height is None or self.resevoir_depth <= 0:
            return None
        percentage = round((height / self.resevoir_depth) * 100, 1)
        return max(0.0, min(100.0, percentage))

    def get_water_level_difference_cm(self):
        distance_cm = self.get_distance_cm()
        if distance_cm is None:
            return None
        return round(self.resevoir_depth - distance_cm, 1)

    def calibrate(self):
        self.resevoir_depth = self.get_distance_cm()
