from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.device_widgets import SchedulerWidget


class SchedulerCard(DeviceCardContent):
    """
    Implements a widget for scheduler management.
    """
    scheduler_widget = ObjectProperty(rebind=True)
    start_button = ObjectProperty()
    clear_button = ObjectProperty()
    next_operation_label = ObjectProperty()
    time_remaining_label = ObjectProperty()

    def __init__(self, scheduler_widget: SchedulerWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.scheduler_widget = scheduler_widget
