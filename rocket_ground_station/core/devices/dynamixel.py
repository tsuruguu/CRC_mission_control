from typing import Callable
from time import time_ns

from rocket_ground_station.core.actions import Feed, Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Dynamixel(Device):
    """
    Implements dynamixel abstraction for interaction with rocket's hardware.
    """

    def __init__(self, open_pos: float, closed_pos: float, velocity: int, **device_kwargs: dict):
        super().__init__(**device_kwargs)
        self._initial_open_pos = open_pos
        self._initial_closed_pos = closed_pos
        self._initial_velocity = velocity
        self._callbacks = []

        self._feeds[ids.OperationID.DYNAMIXEL.value.POSITION].subscribe(
            self._on_position_received)

    def _get_action_data(self) -> dict:
        return {
            Service: {
                self._ids.OPEN: {"data_type": ids.DataTypeID.NO_DATA},
                self._ids.CLOSE: {"data_type": ids.DataTypeID.NO_DATA},
                self._ids.POSITION: {"data_type": ids.DataTypeID.INT16},
                self._ids.OPENED_POS: {"data_type": ids.DataTypeID.INT16},
                self._ids.CLOSED_POS: {"data_type": ids.DataTypeID.INT16},
                self._ids.DISABLE: {"data_type": ids.DataTypeID.NO_DATA},
                self._ids.RESET: {"data_type": ids.DataTypeID.NO_DATA},
                self._ids.VELOCITY: {"data_type": ids.DataTypeID.INT16},
            },
            Feed: {
                self._ids.POSITION: {"data_type": ids.DataTypeID.INT16}
            }
        }

    def _on_position_received(self, value: float):
        timestamp = int(time_ns() / 1000.0)

        for callback in self._callbacks:
            callback(value, timestamp)

    def subscribe(self, callback: Callable = None):
        callback = self._default_callback('Received ') if callback is None else callback
        self._callbacks.append(callback)

    def unsubscribe(self):
        self._callbacks.clear()

    def synchronize(self, on_synchronize: Callable = None) -> None:
        self._synchronizations_left = 3
        self.set_open_pos(self._initial_open_pos, self._service_synchronized)
        self.set_closed_pos(self._initial_closed_pos, self._service_synchronized)
        self.set_velocity(self._initial_velocity, self._service_synchronized)

        super().synchronize(on_synchronize)

    def _service_synchronized(self, ack: bool) -> None:
        if ack:
            self._on_synchronization()

    def open(self, ack_cb: Callable = None) -> None:
        self.set_position(self.open_pos, ack_cb)

    def close(self, ack_cb: Callable = None) -> None:
        self.set_position(self.closed_pos, ack_cb)

    def reset(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Reset acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.RESET].call(on_receive=ack_cb)

    def disable(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Disable acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.DISABLE].call(on_receive=ack_cb)

    def set_position(self, position: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set position acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.POSITION].call(on_receive=ack_cb, data=(position,))

    def set_open_pos(self, position: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set open position acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.OPENED_POS].call(on_receive=ack_cb, data=(position,))

    def set_closed_pos(self, position: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set closed position acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.CLOSED_POS].call(on_receive=ack_cb, data=(position,))

    def set_velocity(self, velocity: int, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback(
            'Set velocity acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.VELOCITY].call(on_receive=ack_cb, data=(velocity,))

    def subscribe_to_position(self, callback: Callable) -> None:
        self._feeds[self._ids.POSITION].subscribe(callback)


    @property
    def initial_velocity(self) -> int:
        return self._initial_velocity

    @property
    def position(self) -> int:
        return self._feeds[ids.OperationID.DYNAMIXEL.value.POSITION].last_received_value

    @property
    def velocity(self) -> int:
        initial_velocity = self._initial_velocity
        velocity = self._services[self._ids.VELOCITY].last_acknowledged_value
        return velocity if velocity is not None else initial_velocity

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
