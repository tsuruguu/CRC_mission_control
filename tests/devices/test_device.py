# pylint: disable=protected-access, attribute-defined-outside-init
import unittest
from unittest.mock import Mock
from rocket_ground_station.core.actions import Request
from rocket_ground_station.core.communication import CommunicationManager, ids
from rocket_ground_station.core.devices import Device

# devices init subclass uses assigns type id to device based on enums with type ids.
# we can't mutate that enum because it is in another closure, so we remove device
# __init_subclass__ handler and assign id manually
MOCK_DEVICE_ID = 1
Device.__init_subclass__ = object.__init_subclass__


class MockDevice(Device):
    type_id = MOCK_DEVICE_ID

    def __init__(self):
        example_board = ids.BoardID.KROMEK.name
        example_id = 1
        super().__init__(example_board, device_id=example_id, name='name',
                         communication=Mock(spec=CommunicationManager))

    def _get_action_data(self) -> dict:
        example_request_id = 1
        return {
            Request: {
                example_request_id: {},
            },
        }


class TestDevice(unittest.TestCase):
    def setUp(self):
        self.device = MockDevice()

    def test_if_synchronize_calls_on_synchronization_callback(self):
        # Assign
        on_synchronization_callback = Mock()
        # Act
        self.device.synchronize(on_synchronization_callback)
        # Assert
        on_synchronization_callback.assert_called_once()

    def setup_mock_requests(self):
        self._mocked_request = Mock(spec=Request)
        self._mocked_requests = {
            'example_request': self._mocked_request
        }
        self.device._requests = self._mocked_requests


if __name__ == '__main__':
    unittest.main()
