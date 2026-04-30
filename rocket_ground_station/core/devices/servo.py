from typing import Callable

from rocket_ground_station.core.actions import Request, Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Servo(Device):
    """
    Implements servo abstraction for interaction with rocket's hardware.
    """

    def __init__(self, open_pos: int, closed_pos: int, **device_kwargs: dict):
        super().__init__(**device_kwargs)
        self._initial_open_pos = open_pos
        self._initial_closed_pos = closed_pos

    def _get_action_data(self) -> dict:
        return {
            Service: {
                self._ids.OPEN: {"data_type": ids.DataTypeID.NO_DATA},
                self._ids.CLOSE: {"data_type": ids.DataTypeID.NO_DATA},
                self._ids.POSITION: {"data_type": ids.DataTypeID.INT16},
                self._ids.OPENED_POS: {"data_type": ids.DataTypeID.INT16},
                self._ids.CLOSED_POS: {"data_type": ids.DataTypeID.INT16},
            },
            Request: {
                self._ids.POSITION: {}
            }
        }

    def synchronize(self, on_synchronize: Callable = None) -> None:
        self._synchronizations_left = 2
        self.set_open_pos(self._initial_open_pos, self._service_synchronized)
        self.set_closed_pos(self._initial_closed_pos, self._service_synchronized)
        super().synchronize(on_synchronize)

    def _service_synchronized(self, ack: bool) -> None:
        if ack:
            self._on_synchronization()

    def open(self, ack_cb: Callable = None) -> None:
        self.set_position(self.open_pos, ack_cb)

    def close(self, ack_cb: Callable = None) -> None:
        self.set_position(self.closed_pos, ack_cb)

    def set_position(self, position: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set position acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.POSITION].call(on_receive=ack_cb, data=(position,))

    def read_position(self, callback: Callable = None) -> None:
        callback = self._default_callback(
            'Current position: ') if callback is None else callback
        self._requests[self._ids.POSITION].request(on_receive=callback)

    def set_open_pos(self, position: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set open position acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.OPENED_POS].call(on_receive=ack_cb, data=(position,))

    def set_closed_pos(self, position: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set closed position acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.CLOSED_POS].call(on_receive=ack_cb, data=(position,))

    @property
    def position(self) -> int:
        return self._services[self._ids.POSITION].last_acknowledged_value

    @property
    def open_pos(self) -> int:
        initial_pos = self._initial_open_pos
        pos = self._services[self._ids.OPENED_POS].last_acknowledged_value
        return pos if pos is not None else initial_pos

    @property
    def closed_pos(self) -> int:
        initial_pos = self._initial_closed_pos
        pos = self._services[self._ids.CLOSED_POS].last_acknowledged_value
        return pos if pos is not None else initial_pos

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({self.name!r}, {self.board!r}, '
                f'{self.id!r}, {self.closed_pos!r}, {self.open_pos!r})')
