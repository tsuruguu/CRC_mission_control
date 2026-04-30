from kivy.properties import ObjectProperty, ListProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.components.tabs import Communication


class ConnectionButton(MDBoxLayout):
    communication_tab = ObjectProperty()
    icon_button = ObjectProperty()
    label = ObjectProperty()
    icon_failure_color = ListProperty()
    icon_success_color = ListProperty()
    icon_initial_color = ListProperty()

    icon_disconnected = 'power-plug-off'
    icon_connected = 'power-plug'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(communication_tab=self.on_communication_tab)

    def on_communication_tab(self, instance, value: Communication) -> None:
        value.bind(on_connection_start=self._activate)
        value.bind(on_connection_stop=self._deactivate)
        value.bind(on_connection_lost=self._deactivate_after_lost_connection)

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.communication_tab is not None:
            if self.communication_tab.is_connected:
                self.communication_tab.disconnect()
            else:
                self.communication_tab.connect()

    def _activate(self, communication_tab):
        self.icon_button.icon = self.icon_connected
        self.icon_button.icon_color = self.icon_success_color

    def _deactivate(self, communication_tab):
        self.icon_button.icon = self.icon_disconnected
        self.icon_button.icon_color = self.icon_initial_color

    def _deactivate_after_lost_connection(self, communication_tab):
        self.icon_button.icon = self.icon_disconnected
        self.icon_button.icon_color = self.icon_failure_color
