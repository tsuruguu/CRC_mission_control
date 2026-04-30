from functools import partial
from kivy.properties import BooleanProperty, DictProperty
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget


class SupplyWidget(DeviceWidget):
    is_open = BooleanProperty(defaultvalue=False)
    ack_states = DictProperty({
        'OPEN': AckStatus.READY,
        'CLOSE': AckStatus.READY
    })

    def __init__(self, device: Device, **kwargs):
        super().__init__(device, **kwargs)
        self.register_event_type('on_open')
        self.register_event_type('on_close')

    def open(self) -> None:
        self.reset_ack_states()
        self.ack_states['OPEN'] = AckStatus.WAITING
        self._device.open(partial(self.dispatch, 'on_open'))

    def on_open(self, ack: bool) -> None:
        self.ack_states['OPEN'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        self.is_open = ack

    def close(self) -> None:
        self.reset_ack_states()
        self.ack_states['CLOSE'] = AckStatus.WAITING
        self._device.close(partial(self.dispatch, 'on_close'))

    def on_close(self, ack: bool) -> None:
        self.ack_states['CLOSE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        self.is_open = not ack
