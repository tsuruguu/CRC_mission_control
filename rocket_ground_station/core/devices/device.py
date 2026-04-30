from functools import partial
from itertools import chain
from typing import Callable
import logging

from rocket_ground_station.core.actions import Feed, Request, Service
from rocket_ground_station.core.communication import CommunicationManager, ids
from rocket_ground_station.core.exceptions import DeviceNotImplementedError


class Device:
    """
    Implements the generic hardware abstraction, used for interaction with rocket devices.
    """
    implemented_devices = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.type_id = ids.DeviceID[str.upper(cls.__name__)]
        cls._ids = ids.OperationID[str.upper(cls.__name__)].value
        Device.implemented_devices[str.lower(cls.__name__)] = cls

    @staticmethod
    def from_type(device_type: str, **kwargs):
        logger = logging.getLogger('main')
        try:
            logger.debug(f'Creating device: {kwargs}')
            return Device.implemented_devices[device_type](**kwargs)
        except KeyError:
            raise DeviceNotImplementedError(
                f'Failed to create a device with type: {device_type}')

    def __init__(self,
                 board: str,
                 device_id: int,
                 name: str,
                 communication: CommunicationManager,
                 snapshotting: bool = False,
                 hydro_name: str = '') -> None:
        self._board = int(ids.BoardID[str.upper(board)])
        self._id = int(device_id)
        self._name = str(name)
        self._synchronizations_left = 0
        self._synchronization_callback = None
        self._services, self._requests, self._feeds = self._create_actions(communication)
        self._hydro_name = str(hydro_name)
        self._is_snapshottable = bool(snapshotting)

    def _create_actions(self, cm: CommunicationManager) -> tuple:
        default_action_data = {Service: {}, Request: {}, Feed: {}}
        action_data = {**default_action_data, **self._get_action_data()}
        return tuple(
            {operation_id: ActionType(device=self, cm=cm, operation=operation_id, **kwargs)
             for operation_id, kwargs in actions.items()}
            for ActionType, actions in action_data.items()
        )

    def _get_action_data(self) -> dict:
        return {}

    def arm(self):
        for operation in chain(self._requests.values(),
                               self._services.values(),
                               self._feeds.values()):
            operation.arm()

    def disarm(self):
        for operation in chain(self._requests.values(),
                               self._services.values(),
                               self._feeds.values()):
            operation.disarm()

    def synchronize(self, on_synchronize: Callable = None) -> None:
        self._synchronization_callback = self._default_callback(
            'Synchronization completed') if on_synchronize is None else on_synchronize
        self._on_synchronization(0)

    def _on_synchronization(self, count: int = -1) -> None:
        self._synchronizations_left += count
        if self._synchronizations_left == 0 and self._synchronization_callback is not None:
            self._synchronization_callback()

    def _default_callback(self, msg: str) -> Callable:
        header = f'[{str.lower(self.__class__.__name__)}s.{self.name}]'
        return partial(print, header, msg)

    @property
    def is_armed(self) -> bool:
        return all(operation.is_armed for operation in chain(self._requests.values(),
                                                             self._services.values(),
                                                             self._feeds.values()))

    @property
    def board(self) -> int:
        return self._board

    @property
    def board_name(self) -> str:
        return ids.BoardID(self.board).name

    @property
    def id(self) -> int:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def hydro_name(self) -> str:
        return self._hydro_name

    @property
    def is_synchronized(self) -> bool:
        return self._synchronizations_left == 0

    @property
    def is_snapshottable(self) -> bool:
        return self._is_snapshottable

    @property
    def service_ids(self) -> tuple:
        return tuple(self._services.keys())

    @property
    def request_ids(self) -> tuple:
        return tuple(self._requests.keys())

    @property
    def feed_ids(self) -> tuple:
        return tuple(self._feeds.keys())

    @property
    def operation_ids(self) -> ids.OperationID:
        return ids.OperationID[type(self).__name__.upper()]

    def __str__(self) -> str:
        return self.__class__.__name__ + '(' + self.name + ')'
