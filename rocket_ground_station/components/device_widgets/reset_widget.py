from functools import partial
from kivy.properties import DictProperty
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget
from rocket_ground_station.components.popups.question import BinaryQuestion


class ResetWidget(DeviceWidget):
    ack_states = DictProperty({
        'RESET': AckStatus.READY,
    })

    def __init__(self, device: Device, **kwargs):
        super().__init__(device, **kwargs)
        self.register_event_type('on_reset')

    def reset(self) -> None:
        def on_reset(reset: bool) -> None:
            if reset:
                self.reset_ack_states()
                self.ack_states['RESET'] = AckStatus.WAITING
                self._device.reset(partial(self.dispatch, 'on_reset'))
        BinaryQuestion(f'Are you sure you want to reset {self.board_name}?', on_reset)

    def on_reset(self, ack: bool) -> None:
        self.ack_states['RESET'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
