from kivy.properties import ObjectProperty

from rocket_ground_station.components.tabs import Communication
from rocket_ground_station.components.space_switch import SpaceSwitch


class ConnectionSwitch(SpaceSwitch):
    communication_tab = ObjectProperty()

    def on_communication_tab(self, instance, value: Communication) -> None:
        value.bind(on_connection_start=self._activate)
        value.bind(on_connection_stop=self._deactivate)
        value.bind(on_connection_lost=self._deactivate)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.communication_tab is not None:
            if self.communication_tab.is_connected:
                self.communication_tab.disconnect()
            else:
                self.communication_tab.connect()

    def _activate(self, communication_tab):
        self.active = True

    def _deactivate(self, communication_tab):
        self.active = False
