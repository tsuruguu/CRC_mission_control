from kivy.properties import StringProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.sequences import Operation


class OperationDisplayer(MDBoxLayout):
    device_type = StringProperty()
    device_name = StringProperty()
    operation_name = StringProperty()
    starts_after = StringProperty()
    payload = StringProperty()

    def __init__(self, operation: Operation, **kwargs) -> None:
        super().__init__(**kwargs)
        self._operation = operation
        self.device_type = operation.device_type.upper()
        self.device_name = operation.device_name.upper()
        self.operation_name = operation.operation.upper()
        self.starts_after = str(operation.starts_after)
        self.payload = str(operation.payload)
