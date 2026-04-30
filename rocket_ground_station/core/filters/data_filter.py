from abc import ABC, abstractmethod


class DataFilter(ABC):
    @abstractmethod
    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def filter(self, x: float) -> float:
        pass
