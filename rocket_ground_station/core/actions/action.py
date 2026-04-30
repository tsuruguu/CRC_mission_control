from abc import ABC, abstractmethod

from rocket_ground_station.core.actions.exceptions import DisarmedActionCallError
from rocket_ground_station.core.communication import CommunicationManager, Frame, ids


class Action(ABC):
    """
    Implements an abstraction for interaction with frames callbacks.
    """

    def __init__(self,
                 device,
                 cm: CommunicationManager,
                 operation: ids.OperationID,
                 priority: ids.PriorityID = ids.PriorityID.LOW,
                 data_type: ids.DataTypeID = ids.DataTypeID.INT32) -> None:
        """
        :param device: device to which this action is binded
        :param cm: instance of application's communication interface
        :param operation: id of the operation performed on the device
        :param priority: level of how important the information is
        :param data_type: type of data that is being sent (e.g. int32 or float)
        """
        self._is_armed = True
        self.cm = cm
        self.frame_kwargs = {
            'destination': int(device.board),
            'priority': int(priority),
            'action': int(ids.ActionID[str.upper(self.__class__.__name__)]),
            'source': int(ids.BoardID.GRAZYNA),
            'device_type': int(device.type_id),
            'device_id': int(device.id),
            'data_type': int(data_type),
            'operation': int(operation)
        }

    def arm(self) -> None:
        self._is_armed = True

    def disarm(self) -> None:
        self._is_armed = False

    @abstractmethod
    def on_receive(self, frame: Frame) -> None:
        """
        This method is called when a frame matching to this action is received.
        :param frame: frame received by a communication interface
        """

    def _act(self) -> None:
        if not self._is_armed:
            raise DisarmedActionCallError(action_name=self.frame_kwargs['action'],
                                          operation=self.frame_kwargs['operation'])

    @property
    def is_armed(self) -> bool:
        return self._is_armed
