from typing import Callable, Union

from rocket_ground_station.core.actions.action import Action
from rocket_ground_station.core.communication import Frame


class Feed(Action):
    """
    Implements an action that updates the data when receiving a frame.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._latest_value = None
        self._callbacks = []
        self.cm.register_callback(self.on_receive, Frame(**self.frame_kwargs))

    def on_receive(self, frame: Frame) -> None:
        """
        Updates feed's value to payload of the received frame.
        :param frame: received frame
        """
        self._latest_value = frame.data
        for callback in self._callbacks:
            callback(frame.data)

    def subscribe(self, callback: Callable) -> None:
        """
        Submits a callback to call whenever a new value has been received.
        :param callback: a callable to call with the new value
        """
        self._callbacks.append(callback)

    @property
    def last_received_value(self) -> Union[tuple, float, int]:
        """
        Property returning the most recent received value.
        """
        return self._latest_value
