from kivy.properties import ObjectProperty, StringProperty
from kivy.utils import get_color_from_hex
from kivy.app import App
from rocket_ground_station.components.device_cards.device_card_content import (
    DeviceCardContent,
)
from rocket_ground_station.components.device_widgets.heating_lamp_widget import (
    HeatingLampWidget,
)


class HeatingLampCard(DeviceCardContent):
    """
    Implements a widget for heating lamp management.
    """

    heating_lamp_widget = ObjectProperty(rebind=True)
    pressure_label = ObjectProperty()
    target_pressure_label = ObjectProperty()
    status_label = ObjectProperty()
    target_input = ObjectProperty()
    pressure_units = StringProperty("")

    def __init__(self, heating_lamp_widget: HeatingLampWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self.heating_lamp_widget = heating_lamp_widget
        self.theme_cls = App.get_running_app().theme_cls
        self.red_color = get_color_from_hex("#F44336")

        # Handle state changes
        self.heating_lamp_widget.bind(is_on=self.update_status_label)
        self.heating_lamp_widget.bind(current_pressure=self.update_pressure_label)
        self.heating_lamp_widget.bind(target_pressure=self.update_target_pressure_label)
        self.heating_lamp_widget.bind(is_auto_control_active=self.update_status_label)
        self.heating_lamp_widget.bind(on_sensor_set=self._on_sensor_set)

        # Update initial UI values
        self.update_pressure_label()
        self.update_target_pressure_label()
        self.update_status_label()

    def _on_sensor_set(self, *args):
        self.pressure_units = self.heating_lamp_widget.pressure_units
        self.update_pressure_label()
        self.update_target_pressure_label()

    def update_pressure_label(self, *args):
        """Update the current pressure display."""
        if hasattr(self, "pressure_label") and self.pressure_label:
            value = self.heating_lamp_widget.current_pressure
            self.pressure_label.text = f"{value:.2f} {self.pressure_units}"

            # Update the color based on how close to target value
            self.pressure_label.color = self._get_pressure_color(value)

    def _get_pressure_color(self, current_value):
        """Determine the color for the pressure label based on proximity to target."""
        if not hasattr(self.heating_lamp_widget, "as_heating_lamp"):
            return self.theme_cls.primary_light

        target = self.heating_lamp_widget.target_pressure
        margin = self.heating_lamp_widget.as_heating_lamp.margin

        # Define thresholds for color changes
        close_threshold = target * 0.1  # Very close to target
        within_margin_threshold = margin  # Within the margin

        diff = abs(current_value - target)

        if diff <= within_margin_threshold:
            # Within margin - use primary light
            return self.theme_cls.primary_light

        if diff <= close_threshold:
            # Very close to target - use accent color
            return self.theme_cls.accent_color

        # Far outside margin - use red
        return self.red_color  # Material Design red

    def update_target_pressure_label(self, *args):
        """Update the target pressure display."""
        if hasattr(self, "target_pressure_label") and self.target_pressure_label:
            value = self.heating_lamp_widget.target_pressure
            self.target_pressure_label.text = f"{value:.2f} {self.pressure_units}"

            # Also update the input field to keep it in sync
            if hasattr(self, "target_input") and self.target_input:
                self.target_input.text = f"{value:.2f}"

    def update_status_label(self, *args):
        """Update the status display."""
        if hasattr(self, "status_label") and self.status_label:
            if self.heating_lamp_widget.is_auto_control_active:
                mode = "AUTO"
            else:
                mode = "MANUAL"

            if self.heating_lamp_widget.is_on:
                status = "ON"
            else:
                status = "OFF"

            self.status_label.text = f"{mode} - {status}"

    def on_target_input_validate(self, value):
        """Handle validation of target pressure input."""
        try:
            # Convert to float, apply it to the device
            target = float(value)
            self.heating_lamp_widget.set_target_pressure(target)

            # Update the display with the processed value
            self.update_target_pressure_label()

        except ValueError:
            # If input isn't a valid number, revert to current target value
            self.target_input.text = str(self.heating_lamp_widget.target_pressure)

    @property
    def is_excluded_from_arming(self) -> bool:
        return False

    @property
    def is_excluded_from_syncing(self) -> bool:
        # Syncing doesn't affect the heating lamp
        return True

    @property
    def requires_large_card(self) -> bool:
        return True
