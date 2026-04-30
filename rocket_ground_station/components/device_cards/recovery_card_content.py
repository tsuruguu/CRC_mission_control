from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.device_widgets import RecoveryWidget
from rocket_ground_station.components.space_ack_light import SpaceAckLight


class RecoveryCard(DeviceCardContent):
    """
    Implements a widget for recovery management.
    """
    recovery_widget = ObjectProperty(rebind=True)
    arm_button = ObjectProperty()
    disarm_button = ObjectProperty()
    armed_light: SpaceAckLight = ObjectProperty()

    def __init__(self, recovery_widget: RecoveryWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.recovery_widget = recovery_widget
        recovery_widget.bind(on_is_armed=self._update_armed_light)

    def _update_armed_light(self, caller: Widget, is_armed: bool) -> None:
        self.armed_light.set_ack(is_armed)
