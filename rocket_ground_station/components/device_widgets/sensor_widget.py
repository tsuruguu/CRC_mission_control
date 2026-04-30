from functools import partial

from datetime import datetime

from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock

from rocket_ground_station.core.devices import Device
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget


class SensorWidget(DeviceWidget):
    value = NumericProperty(-69) # need this so the first value is for sure different from the default value
    timestamp = NumericProperty()
    rounded_value = NumericProperty(-69)
    round_to = NumericProperty()
    is_unresponsive = BooleanProperty(False)
    tooltip_text = StringProperty('')

    SENSOR_TIMEOUT = 5

    def __init__(self, device: Device):
        super().__init__(device)
        self.register_event_type('on_new_value')
        self.round_to = self._device.round_to
        self._device.subscribe(partial(self.dispatch, 'on_new_value'))
        self._response_timeout_event = None

    def on_new_value(self, value: float, timestamp: int) -> None:
        self.value = value
        if self.round_to > 0:
            self.rounded_value = round(value, self.round_to)
        elif self.round_to == 0:
            self.rounded_value = int(round(value, self.round_to))
        else:
            self.rounded_value = value
        self.timestamp = timestamp

        self.tooltip_text = f'Last update: {datetime.fromtimestamp(self.timestamp//1000000)}'
        self._start_response_timeout()

    def _set_unresponsive(self, _) -> None:
        self.is_unresponsive = True

    def _start_response_timeout(self) -> None:
        self.is_unresponsive = False
        if self._response_timeout_event:
            self._response_timeout_event.cancel()
        self._response_timeout_event = Clock.schedule_once(self._set_unresponsive, self.SENSOR_TIMEOUT)

    @property
    def units(self) -> None:
        return self._device.units

    @property
    def name(self) -> None:
        return self._device.name

    @property
    def recordings(self) -> tuple:
        return tuple(self._device.recordings)

    @property
    def timestamps(self) -> tuple:
        return tuple(self._device.timestamps)
