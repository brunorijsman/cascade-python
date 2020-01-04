import math

class Aggregate:

    def __init__(self):
        self._count = 0
        self._sum = 0
        self._square_sum = 0
        self.zulu = 1

    def record_value(self, value):
        self._count += 1
        self._sum += value
        self._square_sum += value * value

    def average(self):
        if self._count == 0:
            return math.nan
        return self._sum / self._count

    def deviation(self):
        # TODO: Get the right formula
        if self._count < 2:
            return math.nan
        return self._square_sum / self._count

    def to_json_encodeable_object(self):
        return {'average': self.average(), 'deviation': self.deviation()}
