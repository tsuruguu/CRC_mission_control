from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ObjectProperty, OptionProperty
from rocket_ground_station.core.communication.ids import AckStatus


class SpaceServiceButton(MDBoxLayout):
    text = StringProperty()
    callback = ObjectProperty()
    button = ObjectProperty()
    ack = ObjectProperty()
    ack_state = OptionProperty(AckStatus.READY, options=AckStatus)
    spinner = ObjectProperty()

    def _on_button_pressed(self):
        self.callback()

    def on_ack_state(self, instance, value):
        self.ack.set_state(value)
