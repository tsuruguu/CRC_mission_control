from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.device_widgets import SupplyWidget


class SupplyCard(DeviceCardContent):
    """
    Implements a widget for supply management.
    """
    supply_widget = ObjectProperty(rebind=True)
    open_button = ObjectProperty()
    close_button = ObjectProperty()

    def __init__(self, supply_widget: SupplyWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.supply_widget = supply_widget
