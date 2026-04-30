from typing import Callable, Tuple, Union
from collections import deque
from numbers import Number

from rocket_ground_station.core.actions.action import Action
from rocket_ground_station.core.communication import Frame, ids


class Service(Action):
    """
    Implements an action that allows user to send an operation and receive acknowledgement.
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._last_acknowledged_value = None
        self.callbacks = {}
        ack_kwargs = {**self.frame_kwargs, 'action': int(ids.ActionID.ACK)}
        nack_kwargs = {**self.frame_kwargs, 'action': int(ids.ActionID.NACK)}

        self.cm.register_callback(self.on_receive, Frame(**ack_kwargs))
        self.cm.register_callback(self.on_receive, Frame(**nack_kwargs))

    def on_receive(self, frame: Frame) -> None:
        """
        Checks if the service was acknowledged and calls the associated callbacks.
        :param frame: received frame
        """
        assert frame.action in (
            int(ids.ActionID['ACK']), int(ids.ActionID['NACK']))
        acknowledged = bool(frame.action == int(ids.ActionID['ACK']))
        try:
            callback = self.callbacks[frame.data].popleft()
            if len(self.callbacks[frame.data]) == 0:
                del self.callbacks[frame.data]
        except IndexError:
            pass
        else:
            if acknowledged:
                self._last_acknowledged_value = frame.data
            callback(acknowledged)

    def call(self, on_receive: Callable, data: Tuple[Number] = ()) -> None:
        """
        Sends service and adds a callback to call when data is received.
        :param on_receive: function to call with acknowledgement
        :param data: data to send as a payload
        """
        self._act(on_receive=on_receive, data=data)

    # pylint: disable=arguments-differ
    def _act(self, on_receive: Callable, data: Tuple[Number]) -> None:
        super()._act()
        frame = Frame(**self.frame_kwargs, payload=data)
        self.callbacks.setdefault(frame.data, deque()).append(on_receive)
        self.cm.push(frame)

    def add_callback_manually(self, on_receive: Callable, data: Tuple[Number] = ()) -> None:
        """
        Adds a callback manually.
        :param on_receive: function to call with acknowledgement
        :param data: data to send as a payload
        """
        self.callbacks.setdefault(data, deque()).append(on_receive)

    @property
    def last_acknowledged_value(self) -> Union[float, tuple]:
        return self._last_acknowledged_value
