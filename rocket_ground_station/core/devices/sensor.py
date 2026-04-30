from time import time_ns
from typing import Callable

from rocket_ground_station.core.actions import Feed
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices.device import Device

from rocket_ground_station.core.filters.data_filter import DataFilter
from rocket_ground_station.core.filters import IdlePass, MovingAverage, CustomExpression


class Sensor(Device):
    def __init__(self,
                 data_type: str,
                 recording: bool,
                 units: str,
                 scale: float,
                 a: float,
                 b: float,
                 round_to: int = -1,
                 data_filter_name: str = 'IdlePass',
                 data_filter_args: dict = None,
                 **device_kwargs):
        self._data_type = ids.DataTypeID[str.upper(data_type)]
        super().__init__(**device_kwargs)
        self._do_recording = bool(recording)
        self._units = str(units)
        self._scale = float(scale)
        self._a = float(a)
        self._b = float(b)
        self._round_to = int(round_to)
        self._recordings = []
        self._timestamps = []
        self._callbacks = []
        self._feeds[ids.OperationID.SENSOR.value.READ].subscribe(
            self._on_value_received)
        if data_filter_args is None:
            data_filter_args = {}
        self.data_filter = self._instantiate_data_filter(data_filter_name, data_filter_args)

    def _get_action_data(self) -> dict:
        op_ids = ids.OperationID.SENSOR.value
        return {
            Feed: {
                op_ids.READ: {"data_type": self._data_type}
            }
        }

    def _get_available_filters(self) -> dict:
        return {
            IdlePass.__name__.lower(): IdlePass,
            MovingAverage.__name__.lower(): MovingAverage,
            CustomExpression.__name__.lower(): CustomExpression

        }

    def _instantiate_data_filter(self, filter_name: str, filter_args: dict) -> DataFilter:
        filter_name = filter_name.lower()
        available_filters = self._get_available_filters()
        if filter_name not in available_filters:
            raise ValueError(f'Invalid filter name: {filter_name}')
        return available_filters[filter_name](**filter_args)

    def _on_value_received(self, value: float):
        timestamp = int(time_ns() / 1000.0)
        scaled_value = self._scale * value
        scaled_value = scaled_value * self._a + self._b
        scaled_value = self.data_filter.filter(scaled_value)
        if self._do_recording:
            self._recordings.append(scaled_value)
            self._timestamps.append(timestamp)
        for callback in self._callbacks:
            callback(scaled_value, timestamp)

    def subscribe(self, callback: Callable = None):
        callback = self._default_callback('Received ') if callback is None else callback
        self._callbacks.append(callback)

    def unsubscribe(self):
        self._callbacks.clear()

    def synchronize(self, on_synchronize: Callable = None) -> None:
        pass

    def arm(self):
        pass

    def disarm(self):
        pass

    @property
    def value(self) -> float:
        value = self._feeds[ids.OperationID.SENSOR.value.READ].last_received_value
        return value if value is None else (self._scale * value) * self._a + self._b

    @property
    def units(self) -> str:
        return self._units

    @property
    def scale(self) -> float:
        return self._scale

    @property
    def round_to(self) -> int:
        return self._round_to

    @property
    def recordings(self) -> tuple:
        return tuple(self._recordings)

    @property
    def timestamps(self) -> tuple:
        return tuple(self._timestamps)

    def __repr__(self) -> str:
        return (f'{self.__class__.__name__}({self.name!r}, {self.board!r}, {self.id!r}, '
                f'{self._data_type!r}, {self._do_recording!r}, {self.units!r}, {self._scale!r})')
