from functools import partial

from kivy.properties import DictProperty, NumericProperty

from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.core.devices import Device
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget


class DynamixelWidget(DeviceWidget):
    position = NumericProperty()
    velocity = NumericProperty()
    ack_states = DictProperty({
        'OPEN': AckStatus.READY,
        'CLOSE': AckStatus.READY,
        'DISABLE': AckStatus.READY,
        'SET_POSITION': AckStatus.READY,
        'SET_OPENED_POS': AckStatus.READY,
        'SET_CLOSED_POS': AckStatus.READY,
        'SET_VELOCITY': AckStatus.READY
    })

    def __init__(self, device: Device):
        super().__init__(device)
        self.register_event_type('on_open')
        self.register_event_type('on_close')
        self.register_event_type('on_disable')
        self.register_event_type('on_set_position')
        self.register_event_type('on_set_open_pos')
        self.register_event_type('on_set_closed_pos')
        self.register_event_type('on_set_velocity')
        self.register_event_type('on_new_position')
        self.velocity = self._device.velocity
        self._device.subscribe(partial(self.dispatch, 'on_new_position'))

    def on_new_position(self, value: float, timestamp: int) -> None:
        self.position = value

    def open(self) -> None:
        self.reset_ack_states()
        self.ack_states['OPEN'] = AckStatus.WAITING
        self._device.open(partial(self.dispatch, 'on_open'))

    def on_open(self, ack: bool) -> None:
        self.ack_states['OPEN'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def close(self) -> None:
        self.reset_ack_states()
        self.ack_states['CLOSE'] = AckStatus.WAITING
        self._device.close(partial(self.dispatch, 'on_close'))

    def on_close(self, ack: bool) -> None:
        self.ack_states['CLOSE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def reset(self) -> None:
        self.reset_ack_states()
        self._device.reset()

    def disable(self) -> None:
        self.reset_ack_states()
        self._device.disable(partial(self.dispatch, 'on_disable'))

    def set_position(self, position: int) -> None:
        self.reset_ack_states()
        self.ack_states['SET_POSITION'] = AckStatus.WAITING
        self._device.set_position(position, partial(self.dispatch, 'on_set_position'))

    def on_set_position(self, ack: bool) -> None:
        self.ack_states['SET_POSITION'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        self.position = self._device.position if self._device.position is not None else self.position

    def set_open_pos(self, position: int) -> None:
        self.ack_states['SET_OPENED_POS'] = AckStatus.WAITING
        self._device.set_open_pos(position, partial(self.dispatch, 'on_set_open_pos'))

    def on_set_open_pos(self, ack: bool) -> None:
        self.ack_states['SET_OPENED_POS'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def set_closed_pos(self, position: int) -> None:
        self.ack_states['SET_CLOSED_POS'] = AckStatus.WAITING
        self._device.set_closed_pos(position, partial(self.dispatch, 'on_set_closed_pos'))

    def on_set_closed_pos(self, ack: bool) -> None:
        self.ack_states['SET_CLOSED_POS'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def set_velocity(self, velocity: int) -> None:
        self.reset_ack_states()
        self.ack_states['SET_VELOCITY'] = AckStatus.WAITING
        self._device.set_velocity(velocity, partial(self.dispatch, 'on_set_velocity'))

    def on_set_velocity(self, ack: bool) -> None:
        self.ack_states['SET_VELOCITY'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        self.velocity = self._device.velocity if self._device.velocity is not None else self.velocity

    def on_disable(self, ack: bool) -> None:
        self.ack_states['DISABLE'] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED

    def handle_widget_refreshes(self):
        self.velocity = self._device.velocity if self._device.velocity is not None else self.velocity

    @property
    def open_pos(self) -> int:
        return self._device.open_pos

    @property
    def closed_pos(self) -> int:
        return self._device.closed_pos

    @property
    def initial_velocity(self) -> int:
        return self._device.initial_velocity
