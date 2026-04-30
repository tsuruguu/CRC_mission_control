from typing import Union

from kivy.properties import DictProperty
from kivymd.uix.floatlayout import MDFloatLayout

from rocket_ground_station.components.device_widgets import DeviceWidget
from rocket_ground_station.components.visuals.visual import Visual


class HydroVisualisation(MDFloatLayout):
    device_widgets = DictProperty()
    tabs = DictProperty()

    def get_device_widget_from_hydro_name(self, hydro_name: str) -> Union[DeviceWidget, None]:
        for widget in self.device_widgets.values():
            if widget.as_device().hydro_name == hydro_name:
                return widget
        return None

    def match_visuals_to_device_widgets(self) -> None:
        for child in self.children:
            if isinstance(child, Visual):
                device_widget = self.get_device_widget_from_hydro_name(child.name)
                child.device_widget = device_widget
