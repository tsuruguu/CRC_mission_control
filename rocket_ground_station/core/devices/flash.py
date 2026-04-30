from typing import Callable

from rocket_ground_station.core.actions import Service
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device


class Flash(Device):

    def _get_action_data(self) -> dict:
        op_ids = ids.OperationID.FLASH.value
        return {
            Service: {
                op_ids.ERASE: {},
                op_ids.PURGE: {},
                op_ids.START_LOGGING: {},
                op_ids.STOP_LOGGING: {}
            }
        }

    def erase(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Erase acknowledge: ') if ack_cb is None else ack_cb
        self._services[ids.OperationID.FLASH.value.ERASE].call(on_receive=ack_cb)

    def purge(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Purge acknowledge:') if ack_cb is None else ack_cb
        self._services[ids.OperationID.FLASH.value.PURGE].call(on_receive=ack_cb)

    def start_logging(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Start logging acknowledge:') if ack_cb is None else ack_cb
        self._services[ids.OperationID.FLASH.value.START_LOGGING].call(on_receive=ack_cb)

    def stop_logging(self, ack_cb: Callable = None) -> None:
        ack_cb = self._default_callback('Stop logging acknowledge:') if ack_cb is None else ack_cb
        self._services[ids.OperationID.FLASH.value.STOP_LOGGING].call(on_receive=ack_cb)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r}, {self.board!r}, {self.id!r})'
