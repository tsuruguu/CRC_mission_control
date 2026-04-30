from kivy.properties import ObjectProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent
from rocket_ground_station.components.popups.question import Question
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.components.device_widgets import ServoWidget


class ServoCard(DeviceCardContent):
    """
    Implements a widget for servo management.
    """
    servo_widget = ObjectProperty(rebind=True)
    position_bar = ObjectProperty()
    open_button = ObjectProperty()
    close_button = ObjectProperty()
    close_label = ObjectProperty()
    open_label = ObjectProperty()
    position_button = ObjectProperty()
    position_entry = ObjectProperty()

    def __init__(self, servo_widget: ServoWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.servo_widget = servo_widget

    def on_disabled(self, instance, value) -> None:
        if value:
            self._disable()
        else:
            self._enable()

    def _enable(self, caller=None) -> None:
        self.close_label.text = str(self.servo_widget.closed_pos)
        self.open_label.text = str(self.servo_widget.open_pos)

    def _disable(self, caller=None) -> None:
        self.close_label.text = '--'
        self.open_label.text = '--'

    def get_progress_bar_percent(self, widget) -> int:
        try:
            open_by = abs(self.servo_widget.position - self.servo_widget.closed_pos)
            servo_range = abs(self.servo_widget.open_pos - self.servo_widget.closed_pos)
            open_by_percent = int(100 * (open_by/servo_range))
        except TypeError:
            return 0
        return open_by_percent

    def set_position(self):
        open_pos = self.servo_widget.open_pos
        closed_pos = self.servo_widget.closed_pos
        position = int(self.position_entry.text)
        if open_pos >= position >= closed_pos or closed_pos >= position >= open_pos:
            self.servo_widget.set_position(position)
        else:
            def answer(value):
                if value == "YES":
                    if open_pos > closed_pos:
                        if position > open_pos:
                            self.servo_widget.set_open_pos(position)
                            self.open_label.text = str(position)
                        else:
                            self.servo_widget.set_closed_pos(position)
                            self.close_label.text = str(position)
                    else:
                        if position < open_pos:
                            self.servo_widget.set_open_pos(position)
                            self.open_label.text = str(position)
                        else:
                            self.servo_widget.set_closed_pos(position)
                            self.close_label.text = str(position)
                    self.servo_widget.set_position(position)

            if not 32767 > position > -32768:
                Message("Out of range", "Entered value is outside of 16-bit signed integer value range")
                return
            question_text = "The value you have entered is outside of position range for this device, " \
                            "would you like to continue anyway?"
            Question(question_text, answer, ["NO", "YES"])

    @property
    def requires_large_card(self) -> bool:
        return True
