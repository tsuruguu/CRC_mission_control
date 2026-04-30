from functools import partial

from kivy.properties import DictProperty, NumericProperty

from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget


class IgniterWidget(DeviceWidget):
    burntime = NumericProperty()
    ack_states = DictProperty({
        'OFF': AckStatus.READY,
        'IGNITE': AckStatus.READY
    })

    def __init__(self, device: Device, **kwargs):
        super().__init__(device, **kwargs)
        self.burntime = self._device.burntime
        self.register_event_type('on_off')
        self.register_event_type('on_ignite')

    def off(self) -> None:
        self.reset_ack_states()
        self.ack_states['OFF'] = AckStatus.WAITING
        self._device.off(partial(self.dispatch, 'on_off'))

    def on_off(self, ack: bool) -> None:
        self.ack_states['OFF'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def ignite(self) -> None:
        self.reset_ack_states()
        self.ack_states['IGNITE'] = AckStatus.WAITING
        self._device.ignite(partial(self.dispatch, 'on_ignite'))

    def on_ignite(self, ack: bool) -> None:
        self.ack_states['IGNITE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def on_burntime(self, instance, value):
        self._device.burntime = value
