from functools import partial
from kivy.properties import DictProperty
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget
from rocket_ground_station.components.popups.question import BinaryQuestion


class ParachuteWidget(DeviceWidget):
    ack_states = DictProperty({
        'DROGUE': AckStatus.READY,
        'MAIN': AckStatus.READY
    })

    def __init__(self, device: Device, **kwargs):
        super().__init__(device, **kwargs)
        self.register_event_type('on_drogue')
        self.register_event_type('on_main')

    def drogue(self) -> None:
        def on_drogue_deploy(deploy: bool) -> None:
            if deploy:
                self.reset_ack_states()
                self.ack_states['DROGUE'] = AckStatus.WAITING
                self._device.drogue(partial(self.dispatch, 'on_drogue'))
        BinaryQuestion('Are you sure you want to deploy drogue?', on_drogue_deploy)

    def on_drogue(self, ack: bool) -> None:
        self.ack_states['DROGUE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def main(self) -> None:
        def on_main_deploy(deploy: bool) -> None:
            if deploy:
                self.reset_ack_states()
                self.ack_states['MAIN'] = AckStatus.WAITING
                self._device.main(partial(self.dispatch, 'on_main'))
        BinaryQuestion('Are you sure you want to deploy main?', on_main_deploy)

    def on_main(self, ack: bool) -> None:
        self.ack_states['MAIN'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
