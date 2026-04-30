from typing import Dict

from kivy.properties import DictProperty

from rocket_ground_station.components.device_widgets import DeviceWidget
from rocket_ground_station.components.tabs.tab import Tab
from rocket_ground_station.components import hydro_visualisation #pylint: disable=unused-import


class Hydraulics(Tab):
    """
    Implements a tab with interactive hydraulics schematic.
    """
    _device_widgets = DictProperty()

    def __init__(self, **tab_kwargs) -> None:
        super().__init__(**tab_kwargs)
        self._device_widgets = {}
        self._logger.info('Hydraulics tab initialized')

    def on_hardware_load(self, device_widgets: Dict[str, DeviceWidget]) -> None:
        self._device_widgets = device_widgets
        self.ids.hydro_visualisation.match_visuals_to_device_widgets()
