import json
import sys
from abc import ABC, abstractmethod
from inspect import signature
from pathlib import Path
from os import listdir
from os.path import isfile, join, splitext
from typing import Any, Generator, Iterable

import yaml

from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.core.exceptions import (BadConfigFormatError,
                                                   InvalidConfigError)
from rocket_ground_station.core.utils.singleton import Singleton


class Parameters:
    """
    Implements a dict of parameters that can be tested.
    """

    def __init__(self, parameters: dict) -> None:
        self._parameters = parameters
        self._test_param_name = ''

    def update(self, key, value):
        self._parameters[key] = value

    def test(self, param_name: str) -> 'Parameters':
        self._test_param_name = param_name
        return self

    def have_keys(self, keys: Iterable) -> None:
        missing_keys = list(set(keys) - set(self._parameters))
        if missing_keys:
            raise InvalidConfigError('Loaded file is missing following keys: ' +
                                     str(missing_keys)[1:-1])

    def have_no_keys_except(self, keys: Iterable) -> None:
        extra_keys = list(set(self._parameters) - set(keys))
        if extra_keys:
            raise InvalidConfigError('Loaded file with unsupported keys: ' +
                                     str(extra_keys)[1:-1] +
                                     'Supported keys are: ' +
                                     str(keys)[1:-1])

    def is_type(self, param_type: type) -> 'Parameters':
        if not isinstance(self[self._test_param_name], param_type):
            msg = f'"{self._test_param_name}" has to be type {param_type.__name__}'
            raise InvalidConfigError(msg)
        return self

    def is_one_of(self, options: Iterable) -> 'Parameters':
        if not self[self._test_param_name] in set(options):
            msg = f'"{self._test_param_name}" has to be one of {options}'
            raise InvalidConfigError(msg)
        return self

    def is_greater_or_equal_to(self, value: float) -> 'Parameters':
        if self[self._test_param_name] < value:
            msg = f'"{self._test_param_name}" cannot be less than {value}'
            raise InvalidConfigError(msg)
        return self

    def is_subset_of(self, options: Iterable) -> None:
        missing_elements = set(self[self._test_param_name]) - set(options)
        if missing_elements:
            raise InvalidConfigError(f'"{self._test_param_name}" contains '
                                     f'invalid elements: {str(missing_elements)[1:-1]}')

    def __getitem__(self, name: str) -> None:
        return self._parameters[name]

    def __iter__(self) -> Generator:
        return ((key, value) for key, value in self._parameters.items())


class Config(ABC):
    """
    Implements an abstraction of a file with configuration parameters.
    """

    def __init__(self, config_name: str) -> None:
        self._name, self._extension = splitext(config_name)
        self._error_message = ''
        try:
            self._parameters = self._open_config_file()
            self._validate()
        except (FileNotFoundError, InvalidConfigError) as error:
            self._error_message = str(error)

    def update(self, parameter, value):
        self._parameters.update(parameter, value)

    def _open_config_file(self) -> Parameters:
        config_path = join(self.get_path(), self.filename)
        with open(config_path, 'r') as config_file:
            if self.extension == '.json':
                return Parameters(json.load(config_file))
            if self.extension == '.yaml':
                return Parameters(yaml.safe_load(config_file))
            raise InvalidConfigError(f'Invalid config extension: "{self.extension}"')

    def save(self) -> None:
        try:
            if self.extension == '.json':
                config_str = json.dumps(dict(self._parameters), indent=2)
            elif self.extension == '.yaml':
                config_str = yaml.dump(dict(self._parameters), indent=2)
            else:
                raise InvalidConfigError(f'Invalid config extension: "{self.extension}"')
        except TypeError:
            raise BadConfigFormatError()
        with open(join(self.get_path(), self.filename), 'w') as config_file:
            config_file.write(config_str)

    @classmethod
    def get_all_config_names(cls) -> list:
        return [config_name for config_name in listdir(cls.get_path())
                if isfile(join(cls.get_path(), config_name))]

    @property
    def filename(self) -> str:
        return self._name + self._extension

    @property
    def name(self) -> str:
        return self._name

    @property
    def extension(self) -> str:
        return self._extension

    @staticmethod
    @abstractmethod
    def get_path() -> str:
        """
        Property for a path to a directory with a config file
        """

    @property
    def is_invalid(self) -> bool:
        return bool(self._error_message)

    @property
    def error_message(self) -> str:
        return self._error_message

    def as_dict(self) -> dict:
        return dict(self._parameters)

    @abstractmethod
    def _validate(self) -> str:
        """
        Method calling any tests of parameters, raising InvalidConfigError
        """

    def __str__(self) -> str:
        return self.__class__.__name__ + '(' + self.filename + ')'

    def __repr__(self) -> str:
        return self.__class__.__name__ + '(' + str(self._parameters)[1:-1] + ')'

    def __getattr__(self, attr_name: str) -> Any:
        try:
            return self._parameters[attr_name]
        except KeyError:
            raise AttributeError(f"config '{self.__class__.__name__}'"
                                 f"has no parameter '{attr_name}'")


class AppConfig(Config, metaclass=Singleton):
    """
    Implements config with ground station application settings
    """

    def __init__(self, config_name: str = None, implemented_tabs: dict = None) -> None:
        if config_name is None or implemented_tabs is None:
            raise ValueError("AppConfig is a singleton, it must be initialized with proper arguments first")
        self.implemented_tabs = implemented_tabs
        super().__init__(config_name)

    @staticmethod
    def get_path() -> str:
        path = Path(sys.argv[0]).resolve()
        while not path.joinpath('configs').is_dir():
            if path == path.parent:
                raise ValueError('Could not find "configs" directory in the path hierarchy')
            path = path.parent
        path = path.joinpath('configs')
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _validate(self) -> None:
        self._parameters.have_keys(('fullscreen', 'dark_mode', 'font_name', 'tabs',
                                    'default_hardware_config', 'receive_dt', 'send_dt',
                                    'log_level', 'save_logs_to_file', 'log_to_file_dt'))
        self._parameters.test('fullscreen').is_type(bool)
        self._parameters.test('dark_mode').is_type(bool)
        self._parameters.test('font_name').is_one_of(['space', 'times', 'arial', 'comic'])
        self._parameters.test('tabs').is_subset_of(self.implemented_tabs)
        self._parameters.test('default_hardware_config').is_type(str)
        self._parameters.test('receive_dt').is_type(float).is_greater_or_equal_to(0.0)
        self._parameters.test('send_dt').is_type(float).is_greater_or_equal_to(0.0)
        self._parameters.test('log_level').is_one_of(lvl.name for lvl in LogLevel)
        self._parameters.test('save_logs_to_file').is_type(bool)
        self._parameters.test('save_frames_to_file').is_type(bool)
        self._parameters.test('log_to_file_dt').is_type(float).is_greater_or_equal_to(0.0)
        self._parameters.test('log_to_frame_file_dt').is_type(float).is_greater_or_equal_to(0.0)
        self._parameters.test('sequence_expire_time').is_type(float).is_greater_or_equal_to(0.0)


class HardwareConfig(Config):
    """
    Implements config with device parameters
    """

    @staticmethod
    def get_path() -> str:
        path = Path(sys.argv[0]).resolve()
        while not path.joinpath('configs').is_dir():
            if path == path.parent:
                raise ValueError('Could not find "configs" directory in the path hierarchy')
            path = path.parent
        path = path.joinpath('configs', 'hardware_configs')
        if not path.exists():
            raise ValueError(f'Path: {path}, does not exist, please create appropriate directory structure')
        return path

    def _validate(self) -> None:
        devices = Parameters(self.devices)
        devices.have_no_keys_except(Device.implemented_devices)
        for device_type, _ in devices:
            params = Parameters(devices[device_type])
            device_init = Device.implemented_devices[device_type].__init__
            proper_args = set(signature(device_init).parameters.keys())
            for base in Device.implemented_devices[device_type].__mro__:
                proper_args.update(set(signature(base.__init__).parameters.keys()))
                if base == Device:
                    break

            for device_name in devices[device_type]:
                params.test(device_name).is_subset_of(proper_args)
        try:
            self._parameters.have_keys(('sequences',))
        except InvalidConfigError:
            self._parameters.update('sequences', {})

    def __iter__(self) -> Generator:
        return ((device_type, device_name, device_args)
                for device_type, device_data in self.devices.items()
                for device_name, device_args in device_data.items())
