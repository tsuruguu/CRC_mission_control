from rocket_ground_station.core.communication import CommunicationManager
from rocket_ground_station.core.communication.mock_communication_manager import MockCommunicationManager
from rocket_ground_station.core.configs import HardwareConfig
from rocket_ground_station.core.devices import Device

from typing import Type, Union
from enum import Enum

class HardwareArmingStatus(Enum):
    DISARMED = 0
    PARTIALLY_ARMED = 1
    ARMED = 2

class DeviceManager:
    """
    Manages and loads hardware configurations.
    """

    def __init__(self, cm: CommunicationManager) -> None:
        self._devices = None
        self._communication = cm
        self._hardware_config = None

    def load_hardware_config(self, config_name: str) -> None:
        config = HardwareConfig(config_name)
        if config.is_invalid:
            raise ValueError(f'Failed to load hardware config: {config_name}')
        self._communication.clear_callbacks()
        self._hardware_config = config
        devices = self._create_devices(config)
        if isinstance(self._communication, MockCommunicationManager):
            self._communication.set_devices(devices)
        self._devices = devices

    def _create_devices(self, config: HardwareConfig) -> dict:
        return {device_name: Device.from_type(device_type,
                                              name=device_name,
                                              communication=self._communication,
                                              **device_args)
                for device_type, device_name, device_args in config}

    def sync_hardware(self) -> None:
        for device in self._devices.values():
            if device.is_armed:
                device.synchronize()

    def arm_hardware(self) -> None:
        if not self._communication.is_connected:
            raise ConnectionError("Connection must be active in order to synchronize devices"
                                  "\nPlease establish connection with the ground station before proceeding")
        for device in self._devices.values():
            device.arm()

    def disarm_hardware(self) -> None:
        for device in self._devices.values():
            device.disarm()

    @property
    def current_hardware_config_name(self) -> str:
        """
        Returns the name of the currently used hardware config file.
        """
        return self._hardware_config.name

    @property
    def current_devices(self) -> Union[dict, None]:
        """
        Returns dict of current devices
        """
        return self._devices

    @property
    def hardware_arming_status(self) -> HardwareArmingStatus:
        """
        Returns the arming status of the hardware
        """
        armed_status = [device.is_armed for device in self._devices.values()]
        if not self._devices or not any(armed_status):
            return HardwareArmingStatus.DISARMED
        if all(armed_status):
            return HardwareArmingStatus.ARMED
        return HardwareArmingStatus.PARTIALLY_ARMED

    def get_device_by_name(self, device_name: str) -> Union[Device, None]:
        return self._devices.get(device_name, None)

    def get_devices_by_type(self, device_type: Type[Device]) -> list[Device]:
        return [device for device in self._devices.values() if isinstance(device, device_type)]
