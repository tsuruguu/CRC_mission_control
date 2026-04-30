from functools import partial
from kivy.properties import (
    BooleanProperty,
    NumericProperty,
    StringProperty,
    ObjectProperty,
)
from rocket_ground_station.core.devices.heating_lamp import HeatingLamp
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget

class HeatingLampWidget(DeviceWidget):
    """Widget for heating lamp control."""

    is_on = BooleanProperty(defaultvalue=False)
    is_auto_control_active = BooleanProperty(defaultvalue=False)
    target_pressure = NumericProperty(0.0)
    current_pressure = NumericProperty(0.0)
    pressure_sensor = ObjectProperty(None, allownone=True)
    pressure_units = StringProperty("")

    ack_states = {
        "OPEN": AckStatus.READY,
        "CLOSE": AckStatus.READY,
    }

    def __init__(self, device: HeatingLamp, **kwargs):
        super().__init__(device, **kwargs)
        self.register_event_type("on_open")
        self.register_event_type("on_close")

        # Initialize properties from device
        self.target_pressure = device.target_pressure
        self._device.subscribe(self._on_status_update)

        # Monitor device armed state to disable auto control when disarmed
        self.bind(is_device_armed=self._on_device_armed_changed)

    def _on_status_update(self, is_on, current_pressure, target_pressure):
        """Handle status updates from the device."""
        self.is_on = is_on
        self.current_pressure = current_pressure
        self.target_pressure = target_pressure

    def turn_on(self):
        """Turn on the heating lamp manually."""
        self.reset_ack_states()
        self.ack_states["OPEN"] = AckStatus.WAITING
        self._device.open(partial(self.dispatch, "on_open"))

    def on_open(self, ack: bool):
        """Handle open acknowledgment."""
        self.ack_states["OPEN"] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        if ack:
            self.is_on = True

    def turn_off(self):
        """Turn off the heating lamp manually."""
        self.reset_ack_states()
        self.ack_states["CLOSE"] = AckStatus.WAITING
        self._device.close(partial(self.dispatch, "on_close"))

    def on_close(self, ack: bool):
        """Handle close acknowledgment."""
        self.ack_states["CLOSE"] = AckStatus.SUCCESSFUL if ack else AckStatus.FAILED
        if ack:
            self.is_on = False

    def start_auto_control(self):
        """Start automatic pressure control."""
        self._device.start_control()
        self.is_auto_control_active = True

    def stop_auto_control(self):
        """Stop automatic pressure control."""
        self._device.stop_control()
        self.is_auto_control_active = False
        # Explicitly update UI state to show device is OFF
        self.is_on = False

    def set_target_pressure(self, value: float):
        """Set the target pressure for automatic control."""
        self._device.target_pressure = value
        self.target_pressure = value

    @property
    def as_heating_lamp(self) -> HeatingLamp:
        """Get the underlying HeatingLamp device."""
        return self._device

    def _on_device_armed_changed(self, instance, is_armed):
        """Handle changes to the device armed state."""
        if not is_armed:
            if self.is_auto_control_active:
                # Safety feature: Stop auto control when device is disarmed
                self.stop_auto_control()
            else:
                # For manual mode, ensure UI reflects OFF state immediately
                self.is_on = False

            print(f"[{self.name}] Device disarmed, controls disabled")
