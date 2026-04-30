from numbers import Number
from typing import Callable, Tuple

from rocket_ground_station.core.actions.action import Action
from rocket_ground_station.core.communication import Frame, ids


class Request(Action):
    """
    Implements an action that allows user to request the data.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self.callbacks = []
        self._last_received_value = None
        response_kwargs = {**self.frame_kwargs,
                           'action': int(ids.ActionID.RESPONSE)}
        self.cm.register_callback(self.on_receive, Frame(**response_kwargs))

    @property
    def last_received_value(self):
        return self._last_received_value

    def on_receive(self, frame: Frame) -> None:
        """
        Calls the associated callback with received data.
        :param frame: received frame
        """
        for callback in self.callbacks:
            callback(frame.data)
        self.callbacks = []
        self._last_received_value = frame.data

    def request(self, on_receive: Callable, data: Tuple[Number] = ()) -> None:
        """
        Sends a request and adds a callback to call when data is received.
        :param on_receive: function to call with received data
        :param data: data to send as a payload
        """
        self._act(on_receive=on_receive, data=data)

    # pylint: disable=arguments-differ
    def _act(self, on_receive: Callable, data: Tuple[Number]) -> None:
        super()._act()
        frame = Frame(**self.frame_kwargs, payload=data)
        self.callbacks.append(on_receive)
        self.cm.push(frame)
