import unittest

from rocket_ground_station.core.configs import AppConfig
from rocket_ground_station.core.devices import Parachute, Dynamixel
from rocket_ground_station.core.devices.device_manager import DeviceManager
from rocket_ground_station.core.communication.mock_communication_manager import MockCommunicationManager

class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        AppConfig("grazyna_app_config.yaml", {})
        c = MockCommunicationManager()
        c.connect(c.transport_info)
        self.m = DeviceManager(c)
        self.m.load_hardware_config('3ttk_sac.yaml')

    def test_current_hardware_config_name(self):
        self.assertEqual(self.m.current_hardware_config_name, '3ttk_sac')

    def test_get_device_by_name(self):
        self.assertEqual(self.m.get_device_by_name('Bypass').name, 'Bypass')
        self.assertEqual(self.m.get_device_by_name('1234'), None)

    def test_get_devices_by_type(self):
        self.assertEqual(len(self.m.get_devices_by_type(Dynamixel)), 4)
        self.assertEqual(len(self.m.get_devices_by_type(Parachute)), 1)

    def test_get_all_devices(self):
        self.assertEqual(len(self.m.current_devices), 25)
