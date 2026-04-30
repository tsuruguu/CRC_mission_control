from typing import Set, Tuple
from kivy.properties import StringProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.communication.ids import DeviceID


class DeviceDisplayer(MDBoxLayout):
    device_type = StringProperty()
    device_name = StringProperty()
    device_id = StringProperty()
    shown_devices = ObjectProperty()
    device_identifier = ObjectProperty()
    checkbox = ObjectProperty()

    def __init__(self,
                 device_name: str,
                 device_type: str,
                 device_id: int,
                 shown_devices: Set[Tuple[int, int]],
                 **kwargs) -> None:
        super().__init__(**kwargs)
        self.device_name = device_name.upper()
        self.device_type = device_type.upper()
        self.device_id = str(device_id)
        self.shown_devices = shown_devices
        self.device_identifier = (DeviceID[self.device_type].value, device_id)
        self.checkbox.active = self.device_identifier in self.shown_devices

    def on_checkbox_active(self, value: bool) -> None:
        if value:
            self.shown_devices.add(self.device_identifier)
        else:
            self.shown_devices.discard(self.device_identifier)
