from typing import Callable

from rocket_ground_station.core.actions import Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Reset(Device):
    """
    Implements RESET abstraction for interaction with rocket's hardware.
    """

    def _get_action_data(self) -> dict:
        op_ids = ids.OperationID.RESET.value
        return {
            Service: {
                op_ids.RESET: {},
            }
        }

    def reset(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Reset acknowledge: ') if ack_cb is None else ack_cb
        self._services[ids.OperationID.RESET.value.RESET].call(on_receive=ack_cb)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({self.name!r}, {self.board!r}, '
                f'{self.id!r})')
