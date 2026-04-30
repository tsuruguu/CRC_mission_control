from kivy.metrics import dp
from kivy.clock import Clock
from kivy.properties import ListProperty, ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.communication.ids import AckStatus


class SpaceAckLight(MDBoxLayout):
    container_size = ListProperty([dp(60), dp(60)])
    icon = ObjectProperty()
    spinner = ObjectProperty()

    def __init__(self, **kwargs):
        self.timeout_event = Clock.create_trigger(self.on_timeout, 5)
        super().__init__(**kwargs)

    def on_icon(self, instance, value):
        self.switch(self._switch_to_icon)

    def set_state(self, new_state: AckStatus) -> None:
        if new_state == AckStatus.DISABLED:
            self.on_disabled()
        elif new_state == AckStatus.SUCCESSFUL:
            self.on_success()
        elif new_state == AckStatus.WAITING:
            self.on_wait()
        elif new_state == AckStatus.READY:
            self.on_disabled()
        else:
            self.on_fail()

    def on_timeout(self, time):
        self.set_ack(False)

    def set_waiting(self) -> None:
        self.switch(self._switch_to_spinner)

    def set_ack(self, ack: bool) -> None:
        self.icon.text_color = self.icon.ack_color if ack else self.icon.not_ack_color
        self.switch(self._switch_to_icon)

    def on_disabled(self, *args) -> None:
        self.switch(self._switch_to_icon)
        self.icon.text_color = self.icon.disabled_color

    def on_fail(self):
        self.switch(self._switch_to_icon)
        self.icon.text_color = self.icon.not_ack_color
        self.timeout_event.cancel()

    def on_success(self):
        self.switch(self._switch_to_icon)
        self.icon.text_color = self.icon.ack_color
        self.timeout_event.cancel()

    def on_wait(self):
        self.switch(self._switch_to_spinner)
        self.timeout_event()

    def switch(self, switch_action):
        try:
            switch_action()
        except ReferenceError:
            pass

    def _switch_to_icon(self):
        self.icon.text_color = self.icon.disabled_color
        if self.spinner in self.children:
            self.remove_widget(self.spinner)
        if self.icon not in self.children:
            self.add_widget(self.icon)

    def _switch_to_spinner(self):
        if self.icon in self.children:
            self.remove_widget(self.icon)
        if self.spinner not in self.children:
            self.add_widget(self.spinner)
