from kivy.properties import ObjectProperty, ListProperty

from rocket_ground_station.components.buttons import SpaceIconButton


class SyncIndicatorButton(SpaceIconButton):
    device_widget = ObjectProperty(rebind=True)
    synchronize_method = ObjectProperty(rebind=True)
    icon_failure_color = ListProperty()
    icon_success_color = ListProperty()
    icon_initial_color = ListProperty()


    def on_release(self):
        self.synchronize_method()

    def on_device_widget(self, instance, value):
        if self.device_widget is None:
            return
        self.device_widget.bind(is_synchronized=self.on_is_synchronized)
        self.device_widget.bind(is_synchronization_ongoing=self.on_is_synchronization_ongoing)
        self.device_widget.bind(has_attempted_synchronization=self.on_has_attempted_synchronization)

    def update_sync_indicator(self):
        if not self.device_widget.has_attempted_synchronization:
            self.icon_color = self.icon_initial_color
        elif self.device_widget.is_synchronization_ongoing:
            self.icon_color = self.icon_failure_color
        elif not self.device_widget.is_synchronized:
            self.icon_color = self.icon_failure_color
        else:
            self.icon_color = self.icon_success_color

    def on_has_attempted_synchronization(self, instance, value):
        self.update_sync_indicator()

    def on_is_synchronization_ongoing(self, instance, value):
        self.update_sync_indicator()

    def on_is_synchronized(self, instance, value):
        self.update_sync_indicator()
