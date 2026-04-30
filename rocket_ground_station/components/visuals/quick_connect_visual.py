from kivy.properties import StringProperty, ObjectProperty, OptionProperty, DictProperty

from rocket_ground_station.components.device_widgets import RelayWidget
from rocket_ground_station.components.visuals.visual import Visual
from rocket_ground_station.core.communication.ids import AckStatus


class QuickConnectVisual(Visual):
    """Implements a visual representation of a quickConnect for HydroVisualisation"""

    icon_center_pos_hint = ObjectProperty((.0, .0))
    disconnect_button = ObjectProperty()
    connect_button = ObjectProperty()
    button_placement = StringProperty("top")  # top bottom left right
    icon_rotation = StringProperty("horizontal")  # vertical horizontal
    state = StringProperty("unknown")  # disconnected, connected, unknown
    combined_ack = OptionProperty(AckStatus.FAILED, options=AckStatus)  # DISABLED treated as unknown
    ack_states = DictProperty()
    _supported_device_widgets = (RelayWidget,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_size = min(self.size[0], self.size[1]) / 10

    def on_ack_states(self, instance, value):
        new_ack = None
        for status in (AckStatus.SUCCESSFUL, AckStatus.WAITING, AckStatus.FAILED):
            for command in ("OPEN", "CLOSE"):
                received_status = value.get(command)

                if received_status != status:
                    continue
                if status == AckStatus.SUCCESSFUL:
                    if command == "OPEN":
                        self.state = "disconnected"
                    elif command == "CLOSE":
                        self.state = "connected"
                new_ack = status

        self.combined_ack = new_ack if new_ack is not None else AckStatus.DISABLED
