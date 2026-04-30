from kivy.properties import ObjectProperty, ListProperty, NumericProperty
from rocket_ground_station.components.device_cards.device_card_content import DeviceCardContent

from rocket_ground_station.components.device_widgets import PistonWidget


class PistonCard(DeviceCardContent):
    """
    Implements a widget for piston visualisation and management.
    """
    per_value_label = ObjectProperty()
    len_value_label = ObjectProperty()
    vol_value_label = ObjectProperty()
    label_box = ObjectProperty()
    piston_widget = ObjectProperty(rebind=True)
    value_wrong_color = ListProperty()
    value_right_color = ListProperty()
    label_scaling = NumericProperty()

    def __init__(self, piston_widget: PistonWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.piston_widget = piston_widget
        self.piston_widget.on_new_value_callback = self.check_value_size
        self.initialize_labels()

    def initialize_labels(self) -> None:
        self.label_scaling = 1
        if not self.piston_widget.is_len_displayed:
            self.label_scaling += 0.5
            self.label_box.remove_widget(self.len_value_label)
        if not self.piston_widget.is_vol_displayed:
            self.label_scaling += 0.5
            self.label_box.remove_widget(self.vol_value_label)
        self.reset_label_values()

    def reset_label_values(self) -> None:
        self.per_value_label.text = '--'
        if self.piston_widget.is_len_displayed:
            self.len_value_label.text = '--'
        if self.piston_widget.is_vol_displayed:
            self.vol_value_label.text = '--'

    def on_disabled(self, instance, value) -> None:
        self.reset_label_values()

    def check_value_size(self) -> None:
        maxsafe, minsafe = self.piston_widget.get_piston_safe_limits()
        is_piston_safe = self.piston_widget.per_value > maxsafe or self.piston_widget.per_value < minsafe
        color = self.value_wrong_color if is_piston_safe else self.value_right_color
        self.update_label_colors(color)

    def update_label_colors(self, color) -> None:
        self.per_value_label.color = color
        if self.piston_widget.is_len_displayed:
            self.len_value_label.color = color
        if self.piston_widget.is_vol_displayed:
            self.vol_value_label.color = color

    @property
    def is_excluded_from_arming(self) -> bool:
        return True

    @property
    def is_excluded_from_syncing(self) -> bool:
        return True
