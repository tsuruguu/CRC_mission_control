from functools import partial

from kivy.properties import DictProperty

from rocket_ground_station.core.devices import Device
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget
from rocket_ground_station.core.communication.ids import AckStatus


class FlashWidget(DeviceWidget):
    ack_states = DictProperty({
        'START': AckStatus.READY,
        'STOP': AckStatus.READY,
        'ERASE': AckStatus.READY,
        'PURGE': AckStatus.READY
    })

    def __init__(self, device: Device, **kwargs):
        super().__init__(device, **kwargs)
        self.register_event_type('on_erase')
        self.register_event_type('on_purge')
        self.register_event_type('on_start_logging')
        self.register_event_type('on_stop_logging')

    def erase(self) -> None:
        self.ack_states['ERASE'] = AckStatus.WAITING
        self._device.erase(partial(self.dispatch, 'on_erase'))

    def on_erase(self, ack: bool) -> None:
        self.ack_states['ERASE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def purge(self) -> None:
        self.ack_states['PURGE'] = AckStatus.WAITING
        self._device.purge(partial(self.dispatch, 'on_purge'))

    def on_purge(self, ack: bool) -> None:
        self.ack_states['PURGE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def start_logging(self) -> None:
        self.ack_states['START'] = AckStatus.WAITING
        self._device.start_logging(partial(self.dispatch, 'on_start_logging'))

    def on_start_logging(self, ack: bool) -> None:
        self.ack_states['START'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def stop_logging(self) -> None:
        self.ack_states['STOP'] = AckStatus.WAITING
        self._device.stop_logging(partial(self.dispatch, 'on_stop_logging'))

    def on_stop_logging(self, ack: bool) -> None:
        self.ack_states['STOP'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
