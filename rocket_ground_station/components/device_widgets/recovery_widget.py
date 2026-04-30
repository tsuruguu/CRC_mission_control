from functools import partial
from kivy.properties import BooleanProperty, DictProperty
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget


class RecoveryWidget(DeviceWidget):
    is_armed = BooleanProperty(defaultvalue=False)
    ack_states = DictProperty({
        'ARM': AckStatus.READY,
        'DISARM': AckStatus.READY
    })

    def __init__(self, device: Device, **kwargs):
        super().__init__(device, **kwargs)
        self.register_event_type('on_arm_recovery')
        self.register_event_type('on_disarm_recovery')

    def arm_recovery(self) -> None:
        self.reset_ack_states()
        self.ack_states['ARM'] = AckStatus.WAITING
        self._device.arm_recovery(partial(self.dispatch, 'on_arm_recovery'))

    def on_arm_recovery(self, ack: bool) -> None:
        self.ack_states['ARM'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        self.is_armed = ack

    def disarm_recovery(self) -> None:
        self.reset_ack_states()
        self.ack_states['DISARM'] = AckStatus.WAITING
        self._device.disarm_recovery(partial(self.dispatch, 'on_disarm_recovery'))

    def on_disarm_recovery(self, ack: bool) -> None:
        self.ack_states['DISARM'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        self.is_armed = not ack
