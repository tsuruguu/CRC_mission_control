from itertools import chain
from functools import partial
from typing import Callable, List

from rocket_ground_station.core.actions import Service, Schedule
from rocket_ground_station.core.communication import CommunicationManager, ids, Frame
from rocket_ground_station.core.devices.device import Device


class Scheduler(Device):
    """
    Abstraction for sequence management and uploading
    """

    def __init__(self,
                 communication: CommunicationManager,
                 close_on_finish: bool,
                 expect_acks_from: List[str] = None,
                 **device_kwargs) -> None:
        super().__init__(communication=communication, **device_kwargs)
        self._close_on_finish = False  # Feature is broken in the hardware, disabled until fixed
        self._expect_acks_from = {ids.BoardID[board.upper()]
                                  for board in expect_acks_from} if expect_acks_from else set()
        self._cm = communication
        self._frames_to_upload: List[Frame] = []
        self._last_sent_frame = None

    def _get_action_data(self) -> dict:
        return {
            Service: {
                self._ids.START: {'data_type': ids.DataTypeID.UINT8},
                self._ids.CLEAR: {'data_type': ids.DataTypeID.NO_DATA},
                self._ids.ABORT: {'data_type': ids.DataTypeID.NO_DATA},
            }
        }

    def synchronize(self, on_synchronize: Callable = None) -> None:
        self._synchronizations_left = len(self._expect_acks_from)
        self.clear(self._service_synchronized)
        super().synchronize(on_synchronize)

    def _service_synchronized(self, ack: bool) -> None:
        if ack:
            self._on_synchronization()
        else:
            self._on_synchronization(0)

    def start(self, ack_cb: Callable = None) -> None:
        ack_cb = ack_cb or self._default_callback('Start acknowledge: ')
        self._register_broadcast_callbacks(self._ids.START, ack_cb, )
        self._services[self._ids.START].call(
            on_receive=ack_cb, data=(int(self._close_on_finish),))

    def abort(self, ack_cb: Callable = None) -> None:
        ack_cb = ack_cb or self._default_callback('Abort acknowledge: ')
        self._register_broadcast_callbacks(self._ids.ABORT, ack_cb)
        self._services[self._ids.ABORT].call(on_receive=ack_cb)

    def clear(self, ack_cb: Callable = None) -> None:
        ack_cb = ack_cb or self._default_callback('Clear acknowledge: ')
        self._register_broadcast_callbacks(self._ids.CLEAR, ack_cb)
        self._services[self._ids.CLEAR].call(on_receive=ack_cb)

    def upload_sequence(self, sequence: List[Frame],
                        on_upload_cb: Callable[[Frame, int], None] = None) -> None:
        on_upload_cb = on_upload_cb or self._default_callback('Uploaded schedule frame: ')
        self._frames_to_upload = list(sequence)
        self._upload_next_operation(on_upload_cb)

    def disarm(self):
        for operation_id, operation in chain(self._requests.items(),
                                             self._services.items(),
                                             self._feeds.items()):
            if operation_id != self._ids.ABORT:
                operation.disarm()

    def _upload_next_operation(self, on_upload_cb: Callable[[Frame, bool], None]) -> None:
        frame_to_upload = self._frames_to_upload.pop(0)
        on_frame_cb = partial(self._on_schedule_upload, on_upload_cb=on_upload_cb)
        self._create_schedule_action(frame_to_upload).upload(on_frame_cb)
        self._last_sent_frame = frame_to_upload

    def _register_broadcast_callbacks(self, cb_id, ack_cb: Callable):
        for _ in range(len(self._expect_acks_from) - 1):
            self._services[cb_id].add_callback_manually(ack_cb)

    def _create_schedule_action(self, frame: Frame) -> Schedule:
        return Schedule(frame,
                        device=self,
                        cm=self._cm,
                        operation=frame.operation,
                        priority=ids.PriorityID.LOW,
                        data_type=frame.data_type)

    def _on_schedule_upload(self, frame: Frame, ack: bool,
                            on_upload_cb: Callable[[Frame, bool, int], None]) -> None:
        error_msg = f'Unexpected schedule received: {frame}, Expected: {self._last_sent_frame}'
        assert frame.payload == self._last_sent_frame.payload, error_msg
        operations_left = len(self._frames_to_upload)
        on_upload_cb(frame, ack, operations_left)
        if operations_left:
            self._upload_next_operation(on_upload_cb)

    def terminate_sequence_upload(self) -> None:
        self._frames_to_upload = []

    @property
    def close_on_finish(self) -> bool:
        return self._close_on_finish

    @close_on_finish.setter
    def close_on_finish(self, close_on_finish: bool) -> None:
        self._close_on_finish = bool(close_on_finish)

    @property
    def expect_acks_from(self) -> List[str]:
        return self._expect_acks_from

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({self.name!r}, {self.board!r})'
