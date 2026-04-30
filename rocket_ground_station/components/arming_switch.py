from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.input.motionevent import MotionEvent

from rocket_ground_station.components.tabs.hardware import Hardware
from rocket_ground_station.components.space_switch import SpaceSwitch


class ArmingSwitch(SpaceSwitch):
    hardware_tab: Hardware = ObjectProperty()

    def on_hardware_tab(self, caller: Widget, hardware_tab: Hardware) -> None:
        hardware_tab.bind(is_hardware_armed=self._on_hardware_armed)
        self.active = hardware_tab.is_hardware_armed

    def on_touch_down(self, touch: MotionEvent) -> None:
        if self.collide_point(*touch.pos) and self.hardware_tab is not None:
            if self.active:
                self.hardware_tab.disarm_hardware()
            else:
                self.hardware_tab.arm_hardware()

    def _on_hardware_armed(self, caller: Widget, armed_state: bool) -> None:
        self.active = armed_state
