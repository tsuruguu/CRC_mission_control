from kivy.properties import ObjectProperty

from rocket_ground_station.components.buttons import SpaceIconButton


class SelectiveArmingButton(SpaceIconButton):
    device_widget = ObjectProperty(rebind=True)
    cycle_device_arm_method = ObjectProperty(rebind=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_icon()

    def on_device_widget(self, instance, value):
        if self.device_widget is None:
            return
        self.device_widget.bind(is_device_armed=self.on_is_device_armed)

    def update_icon(self):
        if self.device_widget is not None and self.device_widget.is_device_armed:
            self.icon = 'lock-open-variant'
        else:
            self.icon = 'lock'

    def on_is_device_armed(self, instance, value):
        self.update_icon()

    def on_release(self):
        self.cycle_device_arm_method()
        self.update_icon()
