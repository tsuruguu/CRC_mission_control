from rocket_ground_station.core.filters.data_filter import DataFilter


class MovingAverage(DataFilter):
    def __init__(self, buffer_length: int):
        self.buffer_length = buffer_length
        self.values = []

    def filter(self, x: float) -> float:
        self.values.append(x)
        if len(self.values) > self.buffer_length:
            self.values.pop(0)
        return sum(self.values) / len(self.values)
