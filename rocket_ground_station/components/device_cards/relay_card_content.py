from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent

from rocket_ground_station.components.device_widgets import RelayWidget


class RelayCard(DeviceCardContent):
    """
    Implements a widget for relay management.
    """
    relay_widget = ObjectProperty(rebind=True)
    open_button = ObjectProperty()
    close_button = ObjectProperty()

    def __init__(self, relay_widget: RelayWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.relay_widget = relay_widget
