from typing import Callable

from rocket_ground_station.core.actions import Request, Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Igniter(Device):
    """
    Implements igniter abstraction for interaction with rocket's hardware.
    """

    def __init__(self,
                 burntime: int,
                 **device_kwargs):
        super().__init__(**device_kwargs)
        self._burntime = int(burntime)

    def _get_action_data(self) -> dict:
        return {
            Service: {
                self._ids.OFF: {},
                self._ids.IGNITE: {"data_type": ids.DataTypeID.UINT16},
            },
            Request: {
                self._ids.STATUS: {"data_type": ids.DataTypeID.UINT8}
            }
        }

    def off(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Off acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.OFF].call(on_receive=ack_cb)

    def ignite(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Ignite acknowledge: ') if ack_cb is None else ack_cb
        self._services[self._ids.IGNITE].call(on_receive=ack_cb, data=(self.burntime,))

    def read_status(self, callback: Callable = None) -> None:
        callback = self._default_callback('Current status: ') if callback is None else callback
        self._requests[self._ids.STATUS].request(on_receive=callback)

    @property
    def burntime(self) -> int:
        return self._burntime

    @burntime.setter
    def burntime(self, burntime) -> None:
        assert int(burntime) >= 0, "Igniter's burntime cannot be less than 0"
        self._burntime = burntime

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r}, {self.board!r})'
