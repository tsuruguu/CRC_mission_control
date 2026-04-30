from rocket_ground_station.core.filters.data_filter import DataFilter


class IdlePass(DataFilter):
    def __init__(self, **kwargs):
        pass

    def filter(self, x: float) -> float:
        return x
