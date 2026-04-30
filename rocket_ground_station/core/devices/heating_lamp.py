from typing import Callable, Optional

from rocket_ground_station.core.devices.dependency import Dependency, SharedVariable
from rocket_ground_station.core.devices.relay import Relay


class HeatingLamp(Relay, Dependency):
    """
    Implements heating lamp abstraction for maintaining gas pressure by controlling temperature.
    The heating lamp turns on when pressure is below target and off when it's above target.
    """

    def __init__(
        self,
        target_pressure: float = 0.0,
        margin: float = 1.0,
        dependencies=None,
        **device_kwargs,
    ):
        super().__init__(**device_kwargs)
        Dependency.__init__(self, dependencies)
        self._target_pressure = float(target_pressure)
        self._margin = float(margin)  # Prevents rapid on/off cycling
        self._control_active = False
        self._callbacks = []
        self.is_open = False
        self._current_pressure = 0.0
        self._pressure_sensor = SharedVariable("pressure_sensor",
                                               self._update_pressure)

    def _update_pressure(self) -> None:
        """
        Update the current pressure reading.
        This should be called by components that monitor pressure sensors.
        """
        self._current_pressure = self._pressure_sensor.get()

        # Only control the lamp if automatic control is active and device is armed
        if self._control_active and self.is_armed:
            # Turn on if pressure is too low (considering margin)
            if self._current_pressure < self._target_pressure - self._margin:
                if not self.is_open:
                    self.open(lambda *args: None)  # We pass an empty callback
                    self.is_open = True
            # Turn off if pressure is too high (considering margin)
            elif self._current_pressure > self._target_pressure + self._margin:
                if self.is_open:
                    self.close(lambda *args: None)  # We pass an empty callback
                    self.is_open = False

        # If auto control is active but device is not armed, disable auto control
        elif self._control_active and not self.is_armed:
            self._control_active = False

        # Always notify callbacks about the current pressure (even in manual mode)
        for callback in self._callbacks:
            callback(self.is_open, self._current_pressure, self._target_pressure)

    def start_control(self) -> None:
        """Start automatic pressure control."""
        # Safety check - don't start control if device is not armed
        if not self.is_armed:
            print(f"[{self.name}] Cannot start auto control: device is not armed")
            return

        self._control_active = True
        # Immediately apply control logic to current pressure
        self._update_pressure()

    def stop_control(self) -> None:
        """Stop automatic pressure control."""
        self._control_active = False
        # Turn off the lamp when control is stopped for safety
        self.close(lambda *args: None)
        self.is_open = False

        # Immediately notify callbacks about state change after stopping control
        for callback in self._callbacks:
            callback(self.is_open, self._current_pressure, self._target_pressure)

    def subscribe(self, callback: Callable = None) -> None:
        """Subscribe to status updates."""
        callback = (
            self._default_callback("Status changed to ")
            if callback is None
            else callback
        )
        self._callbacks.append(callback)

    def unsubscribe(self, callback: Callable = None) -> None:
        """Unsubscribe from status updates."""
        if callback is None:
            self._callbacks.clear()
        elif callback in self._callbacks:
            self._callbacks.remove(callback)

    def open(self, ack_cb: Optional[Callable] = None) -> None:
        """Turn on the heating lamp manually."""
        super().open(ack_cb)
        self.is_open = True

    def close(self, ack_cb: Optional[Callable] = None) -> None:
        """Turn off the heating lamp manually."""
        super().close(ack_cb)
        self.is_open = False

    @property
    def target_pressure(self) -> float:
        """Get the target pressure."""
        return self._target_pressure

    @target_pressure.setter
    def target_pressure(self, value: float) -> None:
        """Set the target pressure."""
        self._target_pressure = float(value)
        if self._control_active:
            # Re-evaluate with the new target pressure
            self._update_pressure()

    @property
    def margin(self) -> float:
        """Get the margin value."""
        return self._margin

    @margin.setter
    def margin(self, value: float) -> None:
        """Set the margin value."""
        self._margin = float(value)

    @property
    def is_control_active(self) -> bool:
        """Check if automatic control is active."""
        return self._control_active

    @property
    def current_pressure(self) -> float:
        """Get the current pressure reading."""
        return self._current_pressure

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.name!r}, {self.board!r}, "
            f"{self.id!r}, target_pressure={self._target_pressure!r})"
        )
