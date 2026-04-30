from typing import Dict
from functools import partial
from kivy.properties import ObjectProperty, DictProperty, StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.components.sequences.operation_editor import OperationEditor
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.sequences import RocketSequence, Operation


class SequenceEditor(MDBoxLayout):
    operations_container = ObjectProperty()
    sequence_time_label = ObjectProperty()
    _devices: DictProperty({})
    _sequence_name: StringProperty()
    _sequence: RocketSequence = ObjectProperty(RocketSequence('default'))

    def open(self, sequence: RocketSequence, devices: Dict[str, Device]) -> None:
        self._sequence_name = sequence.name
        self._devices = devices
        for operation in sequence:
            self._insert_operation(operation, 0)
        if len(sequence) == 0:
            self._insert_operation(self._create_default_operation(), 0)

    def _remove_operation(self, editor: OperationEditor) -> None:
        self.operations_container.remove_widget(editor)

    def _insert_operation(self, operation: Operation, index: int, *args) -> None:
        operation_widget = OperationEditor(operation.copy(), self._devices)
        operation_widget.bind(
            on_move_up=self._move_operation_up,
            on_move_down=self._move_operation_down,
            on_remove=self._remove_operation,
            on_duplicate=partial(self._insert_operation, operation_widget.operation, 0),
            on_starts_after=self._on_starts_after)
        self.operations_container.add_widget(operation_widget, index=index)
        self._update_sequence_time()

    def _move_operation_up(self, editor: OperationEditor) -> None:
        self._insert_operation(editor.operation, self._index_of(editor) + 2)
        self._remove_operation(editor)

    def _move_operation_down(self, editor: OperationEditor) -> None:
        self._insert_operation(editor.operation, max(self._index_of(editor) - 1, 0))
        self._remove_operation(editor)

    def as_sequence(self) -> RocketSequence:
        editors = reversed(self.operations_container.children)
        return RocketSequence(self._sequence_name, [e.operation.copy() for e in editors])

    def set_sequence_name(self, name: str):
        self._sequence_name = name

    def _index_of(self, editor: OperationEditor) -> int:
        for i, child in enumerate(self.operations_container.children):
            if child is editor:
                return i
        return 0

    def _create_default_operation(self) -> Operation:
        device = next(iter(self._devices.values()))
        return Operation(type(device).__name__.lower(),
                         device.name,
                         next(iter(device.operation_ids.value)).name.lower(),
                         starts_after=0,
                         payload=0)

    def _update_sequence_time(self):
        sequence_time = sum(int(child.starts_after_input.text)
                             for child in self.operations_container.children)
        self.sequence_time_label.text = f'TOTAL TIME: {sequence_time}'

    def _on_starts_after(self, *args):
        self._update_sequence_time()
