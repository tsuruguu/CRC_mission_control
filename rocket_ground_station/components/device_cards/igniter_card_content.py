from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.device_widgets import IgniterWidget


class IgniterCard(DeviceCardContent):
    """
    Implements a widget for igniter management.
    """
    igniter_widget = ObjectProperty(rebind=True)
    off_button = ObjectProperty()
    ignite_button = ObjectProperty()

    def __init__(self, igniter_widget: IgniterWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.igniter_widget = igniter_widget
