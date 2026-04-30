from kivy.properties import NumericProperty, ObjectProperty

from rocket_ground_station.components.device_widgets.sensor_widget import SensorWidget


class PistonWidget(SensorWidget):
    relative_pos = NumericProperty(0)
    per_value = NumericProperty(0)
    len_value = NumericProperty(0)
    vol_value = NumericProperty(0)
    on_new_value_callback = ObjectProperty(None)

    def on_new_value(self, value: float, timestamp: int) -> None:
        super().on_new_value(value, timestamp)
        min_val = self._device.min
        max_val = self._device.max
        pos = max(min_val, value)
        pos = min(pos, max_val)
        self.relative_pos = (pos - min_val) / (max_val - min_val)
        self.per_value = round(self.relative_pos * 100, 2)
        self.len_value = round(self.relative_pos * self._device.len / 10, 2)

        if self._device.show_fuel_volume:
            flipped_relative_pos = 1 - self.relative_pos
            self.vol_value = round(flipped_relative_pos * self._device.vol, 2)
        else:
            self.vol_value = round(self.relative_pos * self._device.vol, 2)

        if self.on_new_value_callback:
            self.on_new_value_callback()

    def get_piston_safe_limits(self):
        return self._device.maxsafe, self._device.minsafe

    @property
    def is_len_displayed(self):
        return self._device.islen

    @property
    def is_vol_displayed(self):
        return self._device.isvol
