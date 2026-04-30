from typing import List, Dict, Iterator, Tuple
from dataclasses import dataclass, asdict
from itertools import accumulate

from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication import Frame, ids


@dataclass
class Operation:
    device_type: str
    device_name: str
    operation: str
    starts_after: int
    payload: int

    def as_frame(self, execution_time: int, devices: Dict[str, Device]) -> Frame:
        device = devices[self.device_name]
        operation, payload = self.check_operation(device)
        return Frame(destination=device.board,
                     priority=ids.PriorityID.LOW,
                     action=ids.ActionID.SCHEDULE,
                     source=int(ids.BoardID.GRAZYNA),
                     device_type=int(device.type_id),
                     device_id=device.id,
                     data_type=int(ids.DataTypeID.UINT16INT16),
                     operation=operation,
                     payload=(execution_time, payload))

    def check_operation(self, device: Device) -> Tuple[int, int]:
        operation = self.operation
        payload = self.payload
        if self.device_type in ["servo", "dynamixel"] and operation in ["open", "close"]:
            payload = {"open": device.open_pos, "close": device.closed_pos}.get(operation)
            operation = "position"
        return int(device.operation_ids.value[operation.upper()]), payload

    def validate(self, devices: Dict[str, Device]) -> bool:
        return (self.device_name in devices and
                type(devices[self.device_name]).__name__.lower() == self.device_type and
                self.operation.upper() in devices[self.device_name].operation_ids.value.__members__)

    def copy(self) -> 'Operation':
        return Operation(**self.as_dict())

    def as_dict(self) -> dict:
        return asdict(self)


class RocketSequence:

    def __init__(self, name: str, operations: List[Operation] = None) -> None:
        self._name = name
        self._operations = list(operations or [])

    @classmethod
    def from_config(cls, name: str, config: List[dict]) -> None:
        return RocketSequence(name, [Operation(**conf) for conf in config])

    def as_frames(self, devices: Dict[str, Device]) -> List[Frame]:
        times = list(accumulate([operation.starts_after for operation in self._operations]))
        return [operation.as_frame(time, devices)
                for operation, time in zip(self._operations, times)]

    def validate(self, devices: Dict[str, Device]) -> bool:
        for operation in self._operations:
            if not operation.validate(devices):
                return False
        return True

    def validate_open_close_parity(self):
        operation_counter = self._operations[:]
        while len(operation_counter) > 0:
            operation = operation_counter[0]
            if operation.device_type not in ["relay", "servo", "dynamixel"] \
                    or operation.operation not in ["open", "close"]:
                operation_counter.remove(operation)
                continue
            pair_found = False
            for other_operation in operation_counter[1:]:
                if operation.device_type != other_operation.device_type:
                    continue
                if operation.device_name != other_operation.device_name:
                    continue
                if not ((operation.operation == "open" and other_operation.operation == "close")
                        or (operation.operation == "close" and other_operation.operation == "open")):
                    continue
                operation_counter.remove(operation)
                operation_counter.remove(other_operation)
                pair_found = True
                break
            if not pair_found:
                return False, operation
        return True, None

    def swap(self, first_index: int, second_index: int) -> None:
        original = self._operations[first_index], self._operations[second_index]
        self._operations[second_index], self._operations[first_index] = original

    def insert(self, index: int, operation: Operation) -> None:
        self._operations.insert(index, operation)

    def pop(self, index: int = None) -> Operation:
        return self._operations.pop(index) if index is not None else self._operations.pop()

    def copy(self) -> 'RocketSequence':
        return RocketSequence(self.name, [operation.copy() for operation in self])

    def check_max_time(self) -> bool:
        time = sum(operation.starts_after for operation in self._operations) <= 65535
        return time

    @property
    def operations(self) -> list[Operation]:
        return self._operations

    @property
    def name(self) -> str:
        return self._name

    def __len__(self) -> int:
        return len(self._operations)

    def __getitem__(self, index) -> Operation:
        return self._operations[index]

    def __iter__(self) -> Iterator[Operation]:
        return (operation for operation in self._operations)
