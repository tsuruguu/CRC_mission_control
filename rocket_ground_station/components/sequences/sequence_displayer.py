from kivy.factory import Factory
from kivy.metrics import dp
from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.sequences import RocketSequence
from rocket_ground_station.components.sequences.operation_displayer import OperationDisplayer


class SequenceDisplayer(MDBoxLayout):
    operations_container = ObjectProperty()

    def display(self, sequence: RocketSequence = None) -> None:
        self.operations_container.clear_widgets()
        if sequence is None:
            self.operations_container.add_widget(Factory.SpaceCenteredLabel(
                text='NO VALID SEQUENCE AVAILABLE\nPLEASE CHANGE THE HARDWARE CONFIG',
                valign='center', size_hint_y=None, height=dp(52)))
        else:
            for operation in sequence:
                operation_widget = OperationDisplayer(operation)
                self.operations_container.add_widget(operation_widget)
