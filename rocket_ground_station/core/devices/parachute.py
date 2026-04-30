from typing import Callable

from rocket_ground_station.core.actions import Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Parachute(Device):
    """
    Implements parachute abstraction for interaction with rocket's hardware.
    """

    def _get_action_data(self) -> dict:
        op_ids = ids.OperationID.PARACHUTE.value
        return {
            Service: {
                op_ids.DROGUE: {},
                op_ids.MAIN: {},
            }
        }

    def drogue(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Drogue acknowledge: ') if ack_cb is None else ack_cb
        self._services[ids.OperationID.PARACHUTE.value.DROGUE].call(on_receive=ack_cb)

    def main(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Main acknowledge: ') if ack_cb is None else ack_cb
        self._services[ids.OperationID.PARACHUTE.value.MAIN].call(on_receive=ack_cb)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({self.name!r}, {self.board!r}, '
                f'{self.id!r})')
