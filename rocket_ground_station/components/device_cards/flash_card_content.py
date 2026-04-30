from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent

from rocket_ground_station.components.device_widgets import FlashWidget


class FlashCard(DeviceCardContent):
    """
    Implements a widget for flash management.
    """
    flash_widget = ObjectProperty(rebind=True)
    start_button = ObjectProperty()
    stop_button = ObjectProperty()
    erase_button = ObjectProperty()

    def __init__(self, flash_widget: FlashWidget, **kwargs):
        super().__init__(**kwargs)
        self.flash_widget = flash_widget
