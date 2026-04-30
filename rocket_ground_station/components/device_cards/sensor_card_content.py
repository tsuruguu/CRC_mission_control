from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.device_widgets import SensorWidget


class SensorCard(DeviceCardContent):
    """
    Implements a widget for sensor management.
    """
    value_label = ObjectProperty()
    sensor_widget = ObjectProperty(rebind=True)

    def __init__(self, sensor_widget: SensorWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.sensor_widget = sensor_widget
        self.value_label.text = '--'

    @property
    def is_excluded_from_arming(self) -> bool:
        return True

    @property
    def is_excluded_from_syncing(self) -> bool:
        return True
