from typing import Dict, Set, Tuple

from kivy.properties import ObjectProperty, DictProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.components.device_displayer import DeviceDisplayer


class DeviceSelector(MDBoxLayout):
    current_devices = DictProperty()
    devices_container = ObjectProperty()
    select_all_checkbox = ObjectProperty()

    def __init__(self,
                 curr: Dict[str, Tuple[str, int]],
                 shown_devices: Set[Tuple[int, int]],
                 **kwargs):
        super().__init__(**kwargs)
        self.current_devices = curr
        self.shown_devices = shown_devices
        self._check_interval = Clock.schedule_interval(self._check_if_all_selected, 0.01)
        self.add_devices()

    def add_devices(self):
        for dev_name, dev_info in self.current_devices.items():
            displayer = DeviceDisplayer(dev_name, dev_info[0], dev_info[1], self.shown_devices)
            self.devices_container.add_widget(displayer)

    def select_all(self, value: bool) -> None:
        if not self.select_all_checkbox.checking:
            for dev in self.devices_container.children:
                dev.checkbox.active = value

    def _check_if_all_selected(self, dt: float) -> None:
        states = [dev.checkbox.active for dev in self.devices_container.children]
        self.select_all_checkbox.checking = True
        self.select_all_checkbox.active = all(states)
        self.select_all_checkbox.checking = False

    def cancel_intervals(self):
        self._check_interval.cancel()
