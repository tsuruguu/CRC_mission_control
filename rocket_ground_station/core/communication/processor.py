from rocket_ground_station.core.communication.frame import Frame
from abc import ABC, abstractmethod


class PreProcessor(ABC):
    def process(self, frame: Frame) -> Frame:
        pass

    @property
    @abstractmethod
    def pattern(self) -> Frame:
        pass


class PostProcessor(ABC):
    def process(self, frame: Frame, previously_matched: bool) -> tuple[Frame, bool]:
        pass

    @property
    @abstractmethod
    def pattern(self) -> Frame:
        pass
