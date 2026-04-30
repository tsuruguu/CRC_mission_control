from typing import Callable

from rocket_ground_station.core.actions import Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Relay(Device):
    """
    Implements relay abstraction for interaction with rocket's hardware.
    """

    def __init__(self, is_reversed: bool = False, **device_kwargs: dict):
        super().__init__(**device_kwargs)
        self._is_reversed = is_reversed

    def _get_action_data(self) -> dict:
        op_ids = ids.OperationID.RELAY.value
        return {
            Service: {
                op_ids.OPEN: {},
                op_ids.CLOSE: {},
            }
        }

    def open(self, ack_cb: Callable = None) -> None:
        if self._is_reversed:
            ack_cb = self._default_callback('Close acknowledge: ') if ack_cb is None else ack_cb
            self._services[ids.OperationID.RELAY.value.CLOSE].call(on_receive=ack_cb)
        else:
            ack_cb = self._default_callback('Open acknowledge: ') if ack_cb is None else ack_cb
            self._services[ids.OperationID.RELAY.value.OPEN].call(on_receive=ack_cb)

    def close(self, ack_cb: Callable = None) -> None:
        if self._is_reversed:
            ack_cb = self._default_callback('Open acknowledge: ') if ack_cb is None else ack_cb
            self._services[ids.OperationID.RELAY.value.OPEN].call(on_receive=ack_cb)
        else:
            ack_cb = self._default_callback('Close acknowledge: ') if ack_cb is None else ack_cb
            self._services[ids.OperationID.RELAY.value.CLOSE].call(on_receive=ack_cb)

    @property
    def is_reversed(self) -> bool:
        return self._is_reversed

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({self.name!r}, {self.board!r}, '
                f'{self.id!r})')
