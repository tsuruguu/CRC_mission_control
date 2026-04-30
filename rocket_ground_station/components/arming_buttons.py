from kivymd.uix.boxlayout import MDBoxLayout
from kivy.properties import StringProperty, ObjectProperty


class ArmingButtons(MDBoxLayout):
    text = StringProperty()
    button = ObjectProperty()
    hardware_tab = ObjectProperty()

    def _arm_hardware(self) -> None:
        self.hardware_tab.arm_hardware()

    def _disarm_hardware(self) -> None:
        self.hardware_tab.disarm_hardware()
