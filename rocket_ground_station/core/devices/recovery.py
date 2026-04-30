from typing import Callable

from rocket_ground_station.core.actions import Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Recovery(Device):

    def _get_action_data(self) -> dict:
        op_ids = ids.OperationID.RECOVERY.value
        return {
            Service: {
                op_ids.ARM: {},
                op_ids.DISARM: {},
            }
        }

    def arm_recovery(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Arm acknowledge: ') if ack_cb is None else ack_cb
        self._services[ids.OperationID.RECOVERY.value.ARM].call(on_receive=ack_cb)

    def disarm_recovery(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Disarm acknowledge: ') if ack_cb is None else ack_cb
        self._services[ids.OperationID.RECOVERY.value.DISARM].call(on_receive=ack_cb)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({self.name!r}, {self.board!r}, '
                f'{self.id!r})')
