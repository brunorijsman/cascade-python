import math

class AggregateStats:

    def __init__(self):
        self._count = 0
        self._sum = 0
        self._square_sum = 0

    def record_value(self, value):
        self._count += 1
        self._sum += value
        self._square_sum += value * value

    def average(self):
        if self._count == 0:
            return math.nan
        return self._sum / self._count

    def deviation(self):
        """
        Compute the corrected standard deviation.
        See https://en.wikipedia.org/wiki/Bessel%27s_correction.

        Returns:
            The corrected standard deviation, or NaN if there are less than 2 samples.
        """
        if self._count < 2:
            return math.nan
        return math.sqrt(self._square_sum / (self._count - 1) -
                         self._sum ** 2 / ((self._count - 1) * self._count))

    def to_json_encodeable_object(self):
        return {'average': self.average(), 'deviation': self.deviation()}
