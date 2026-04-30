from rocket_ground_station.core.communication.frame import Frame
from rocket_ground_station.core.communication.ids import BoardID
from rocket_ground_station.core.communication.processor import PostProcessor
from typing import Any


class ProxySourcePostProcessor(PostProcessor):
    def __init__(self):
        self._pattern = Frame(destination=Any,
                              priority=Any,
                              source=BoardID.GRAZYNA,
                              action=Any,
                              device_type=Any,
                              device_id=Any,
                              data_type=Any,
                              operation=Any,
                              payload=Any,
                              pattern=True)

    @property
    def pattern(self) -> Frame:
        return self._pattern

    def process(self, frame: Frame, previously_matched: bool) -> tuple[Frame, bool]:
        frame_params = frame.as_dict()
        frame_params['source'] = BoardID.PROXY

        return Frame(**frame_params), True


class ProxyDestinationPostProcessor(PostProcessor):
    def __init__(self):
        self._pattern = Frame(destination=BoardID.GRAZYNA,
                              priority=Any,
                              source=Any,
                              action=Any,
                              device_type=Any,
                              device_id=Any,
                              data_type=Any,
                              operation=Any,
                              payload=Any,
                              pattern=True)

    @property
    def pattern(self) -> Frame:
        return self._pattern

    def process(self, frame: Frame, previously_matched: bool) -> tuple[Frame, bool]:
        if previously_matched:
            return Frame, False

        frame_params = frame.as_dict()
        frame_params['destination'] = BoardID.PROXY

        return Frame(**frame_params), True
