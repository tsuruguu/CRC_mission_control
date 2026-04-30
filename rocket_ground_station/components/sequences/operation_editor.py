from typing import Dict

from kivy.properties import ObjectProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.sequences import Operation
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.components.space_dropdown import SpaceDropdown
from rocket_ground_station.components.space_text_field import SpaceTextField

class OperationEditor(MDBoxLayout):
    device_type_dropdown: SpaceDropdown = ObjectProperty()
    device_name_dropdown: SpaceDropdown = ObjectProperty()
    operation_dropdown: SpaceDropdown = ObjectProperty()
    starts_after_input: SpaceTextField = ObjectProperty()
    payload_input: SpaceTextField = ObjectProperty()

    def __init__(self, operation: Operation, devices: Dict[str, Device], **kwargs):
        super().__init__(**kwargs)
        self._operation = operation
        self._devices = devices
        self.register_event_type('on_move_up')
        self.register_event_type('on_move_down')
        self.register_event_type('on_remove')
        self.register_event_type('on_duplicate')
        self.register_event_type('on_starts_after')
        self.set_device_type(self._operation.device_type)
        self.set_starts_after(str(self._operation.starts_after))
        self.set_payload(str(self._operation.payload))

    def set_device_type(self, type_name: str) -> None:
        device_types = {type(device).__name__.lower() for device in self._devices.values()}
        if type_name not in device_types:
            Message(title='xd', message='xd')
            return
        self._operation.device_type = type_name
        self.device_type_dropdown.items = device_types
        self.device_type_dropdown.text = self._operation.device_type
        self.set_device_name(self._operation.device_name)

    def set_device_name(self, device_name: str) -> None:
        device_names = {device.name for device in self._devices.values()
                        if type(device).__name__.lower() == self._operation.device_type}
        if device_name in device_names:
            self._operation.device_name = device_name
        else:
            self._operation.device_name = next(iter(device_names))
        self.device_name_dropdown.items = device_names
        self.device_name_dropdown.text = self._operation.device_name
        self.set_operation_name(self._operation.operation)

    def set_operation_name(self, operation_name: str) -> None:
        operations_enum = self._devices[self._operation.device_name].operation_ids
        device_operations = [op.lower() for op in operations_enum.value.__members__]
        if operation_name in device_operations:
            self._operation.operation = operation_name
        else:
            self._operation.operation = next(iter(device_operations))
        self.operation_dropdown.items = device_operations
        self.operation_dropdown.text = self._operation.operation

    def set_starts_after(self, starts_after: str) -> None:
        try:
            self._operation.starts_after = int(starts_after)
        except ValueError:
            if starts_after:
                msg = f'Time has to be an integer, not {starts_after}!'
            else:
                msg = 'Starts After field cannot be empty!'
            Message(title='Text field error', message=msg)
        self.starts_after_input.text = str(self._operation.starts_after)
        self.dispatch('on_starts_after')

    def set_payload(self, payload: str) -> None:
        try:
            self._operation.payload = int(payload)
        except ValueError:
            if payload:
                msg = f'Payload has to be an integer, not {payload}!'
            else:
                msg = 'Payload field cannot be empty'
            Message(title='Text field error', message=msg)
        self.payload_input.text = str(self._operation.payload)

    def on_move_up(self, *args) -> None:
        pass

    def on_move_down(self, *args) -> None:
        pass

    def on_remove(self, *args) -> None:
        pass

    def on_duplicate(self, *args) -> None:
        pass

    def on_starts_after(self, *args) -> None:
        pass

    @property
    def operation(self) -> Operation:
        return self._operation
