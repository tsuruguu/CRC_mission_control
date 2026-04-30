from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.popups.question import Question
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.components.device_widgets import DynamixelWidget


class DynamixelCard(DeviceCardContent):
    """
    Implements a widget for dynamixel management.
    """
    dynamixel_widget = ObjectProperty(rebind=True)
    position_bar = ObjectProperty()
    open_button = ObjectProperty()
    close_button = ObjectProperty()
    close_label = ObjectProperty()
    open_label = ObjectProperty()
    position_entry = ObjectProperty()
    position_button = ObjectProperty()
    velocity_entry = ObjectProperty()
    velocity_button = ObjectProperty()

    def __init__(self, dynamixel_widget: DynamixelWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dynamixel_widget = dynamixel_widget

    def on_disabled(self, instance, value) -> None:
        if value:
            self._disable()
        else:
            self._enable()

    def _enable(self, caller=None) -> None:
        self.close_label.text = str(self.dynamixel_widget.closed_pos)
        self.open_label.text = str(self.dynamixel_widget.open_pos)

    def _disable(self, caller=None) -> None:
        self.close_label.text = '--'
        self.open_label.text = '--'

    def get_progress_bar_percent(self, widget) -> int:
        try:

            if self.dynamixel_widget.position < self.dynamixel_widget.closed_pos:
                return 0

            if self.dynamixel_widget.position > self.dynamixel_widget.open_pos:
                return 100

            open_by = abs(self.dynamixel_widget.position - self.dynamixel_widget.closed_pos)
            dynamixel_range = abs(self.dynamixel_widget.open_pos - self.dynamixel_widget.closed_pos)
            open_by_percent = int(100 * (open_by / dynamixel_range))
        except TypeError:
            return 0
        return open_by_percent

    def set_position(self):
        open_pos = self.dynamixel_widget.open_pos
        closed_pos = self.dynamixel_widget.closed_pos
        try:
            position = int(self.position_entry.text)
        except ValueError:
            Message("Int conversion error",
                    f"Supplied value: {self.velocity_entry.text} is not a valid number")
            return
        if open_pos >= position >= closed_pos or closed_pos >= position >= open_pos:
            self.dynamixel_widget.set_position(position)
        else:
            def answer(value):
                if value == "YES":
                    if open_pos > closed_pos:
                        if position > open_pos:
                            self.dynamixel_widget.set_open_pos(position)
                            self.open_label.text = str(position)
                        else:
                            self.dynamixel_widget.set_closed_pos(position)
                            self.close_label.text = str(position)
                    else:
                        if position < open_pos:
                            self.dynamixel_widget.set_open_pos(position)
                            self.open_label.text = str(position)
                        else:
                            self.dynamixel_widget.set_closed_pos(position)
                            self.close_label.text = str(position)
                    self.dynamixel_widget.set_position(position)

            if not 32767 > position > -32768:
                Message("Out of range", "Entered value is outside of 16-bit signed integer value range")
                return
            question_text = "The value you have entered is outside of position range for this device, " \
                            "would you like to continue anyway?"
            Question(question_text, answer, ["NO", "YES"])

    def set_velocity(self):
        max_velocity = 1000
        min_velocity = 0
        try:
            velocity = int(self.velocity_entry.text)
        except ValueError:
            Message("Int conversion error",
                    f"Supplied value: {self.velocity_entry.text} is not a valid number")
            return
        if max_velocity >= velocity >= min_velocity:
            self.dynamixel_widget.set_velocity(velocity)
        else:
            def answer(value):
                if value == "YES":
                    self.dynamixel_widget.set_velocity(velocity)

            if not 32767 > velocity > -32768:
                Message("Out of range", "Entered value is outside of 16-bit signed integer value range")
                return
            question_text = "The value you have entered is outside of velocity range (0-1000) " \
                            "for this device, would you like to continue anyway?"
            Question(question_text, answer, ["NO", "YES"])

    def handle_widget_refreshes(self):
        self.velocity_entry.text = str(self.dynamixel_widget.velocity)

    @property
    def requires_large_card(self) -> bool:
        return True
