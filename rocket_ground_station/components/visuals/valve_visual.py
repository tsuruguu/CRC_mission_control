from kivy.properties import StringProperty, ObjectProperty, DictProperty, OptionProperty, NumericProperty

from rocket_ground_station.components.device_widgets import DynamixelWidget, ServoWidget, RelayWidget
from rocket_ground_station.components.visuals.visual import Visual
from rocket_ground_station.core.communication.ids import AckStatus


class ValveVisual(Visual):
    """Implements a visual representation of a valve for HydroVisualisation"""
    icon_center_pos_hint = ObjectProperty((.0, .0))
    open_button = ObjectProperty()
    close_button = ObjectProperty()
    button_placement = StringProperty("right")  # top bottom right left
    icon_rotation = StringProperty("vertical")  # vertical horizontal
    state = StringProperty("unknown")  # open, closed, unknown
    combined_ack = OptionProperty(AckStatus.DISABLED, options=AckStatus)  # DISABLED treated as unknown
    ack_states = DictProperty()
    position = NumericProperty(allownone=True)
    open_pos = NumericProperty(allownone=True)
    closed_pos = NumericProperty(allownone=True)
    _supported_device_widgets = (RelayWidget, DynamixelWidget, ServoWidget)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_ack_states(self, instance, value):
        new_ack = None
        for status in (AckStatus.SUCCESSFUL, AckStatus.WAITING, AckStatus.FAILED):
            for command in ("OPEN", "CLOSE", "SET_POSITION", "SET_OPENED_POS", "SET_CLOSED_POS"):
                received_status = value.get(command)

                if received_status != status:
                    continue
                if status == AckStatus.SUCCESSFUL:
                    if command == "OPEN":
                        self.state = "open"
                    elif command == "CLOSE":
                        self.state = "closed"
                    self.update_state()
                new_ack = status

        self.combined_ack = new_ack if new_ack is not None else AckStatus.DISABLED

    def update_state(self):
        if self.device_widget is not None and isinstance(self.device_widget, (DynamixelWidget, ServoWidget)):
            self.position = self.device_widget.position
            self.open_pos = self.device_widget.open_pos
            self.closed_pos = self.device_widget.closed_pos
            margin = 50

            if None not in (self.closed_pos, self.position, self.open_pos) \
                    and self.combined_ack != AckStatus.FAILED:
                if self.open_pos - margin <= self.position <= self.open_pos + margin:
                    self.state = 'open'
                elif self.closed_pos - margin <= self.position <= self.closed_pos + margin:
                    self.state = 'closed'
                else:
                    self.state = 'unknown'

    def on_position(self, instance, value):
        self.update_state()

    def on_open_pos(self, instance, value):
        self.update_state()

    def on_closed_pos(self, instance, value):
        self.update_state()
