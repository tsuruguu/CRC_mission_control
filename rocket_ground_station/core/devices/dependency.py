from abc import ABC
from typing import Union, Dict, Any, List

from rocket_ground_station.core.devices import Sensor


class SharedVariable:
    def __init__(self, name: str, function: callable) -> None:
        self._name = name
        self._function = function
        self._value = None

    def _update(self, value: Any, device: Sensor) -> None:
        self._value = value
        self._function()

    def bind(self, target: str, devices: Dict[str, Sensor], name: str) -> None:
        if not isinstance(target, str):
            raise TypeError(f"{name} must be a single device name")
        if target not in devices:
            raise KeyError(f"{name} target '{target}' not found in devices")
        tg = devices[target]
        tg.subscribe(lambda v, _, t=tg: self._update(v, t))

    def get(self) -> Any:
        return self._value

    @property
    def name(self) -> str:
        return self._name


class SharedListVariable(SharedVariable):
    def __init__(self, name: str, function: callable) -> None:
        super().__init__(name, function)
        self._value = {}

    def _update(self, value: Any, device: Sensor) -> None:
        self._value[device.name] = value
        self._function()

    def bind(self, target: List[str], devices: Dict[str, Sensor], name: str) -> None:
        if not isinstance(target, list):
            raise TypeError(f"{name} must be a list of devices")
        for t in target:
            super().bind(t, devices, f"Content of {name}")

    def get(self) -> List:
        return list(self._value.values())


class Dependency(ABC):
    def __init__(self, dependencies: Dict[str, Union[str, List[str]]]) -> None:
        self._dependencies = dependencies

    def bind_dependencies(self, devices: Dict[str, Sensor]) -> None:
        shared_variables = [
            attr for attr in self.__dict__.values()
            if isinstance(attr, SharedVariable)
        ]

        for variable in shared_variables:
            if variable.name not in self._dependencies:
                raise KeyError(f"Dependency '{variable.name}' not found in device configuration")

            target = self._dependencies[variable.name]
            variable.bind(target, devices, variable.name)

    @staticmethod
    def load(devices: Dict[str, Sensor]) -> None:
        for device in devices.values():
            if isinstance(device, Dependency):
                device.bind_dependencies(devices)
