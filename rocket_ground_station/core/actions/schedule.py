import logging
from typing import Callable

from rocket_ground_station.core.actions.action import Action
from rocket_ground_station.core.communication import Frame, ids


class Schedule(Action):
    """
    Action, that schedules a sequence
    """

    def __init__(self, frame: Frame, **kwargs):
        super().__init__(**kwargs)
        self._logger = logging.getLogger('main')
        self.frame_kwargs = {**frame.as_dict(), 'action': ids.ActionID.SCHEDULE}
        self._frame = Frame(**self.frame_kwargs)
        self._on_schedule_upload: Callable[[Frame], None] = None
        self._register_callbacks()
        self._on_schedule_upload = None

    def upload(self, ack_cb):
        self._act(ack_cb=ack_cb)

    # pylint: disable=arguments-differ
    def _act(self, ack_cb: Callable) -> None:
        super()._act()
        if self._on_schedule_upload is not None:
            self._on_schedule_upload(False)
        self._on_schedule_upload = ack_cb
        self.cm.push(self._frame)

    def on_receive(self, frame: Frame) -> None:
        assert frame.action in (int(ids.ActionID.SACK), int(
            ids.ActionID.SNACK)), f"Assert unexcepted frame received: {frame}"
        if self._on_schedule_upload:
            is_success = frame.action == ids.ActionID.SACK
            self._on_schedule_upload(frame, is_success)
            self._on_schedule_upload = None

    def _register_callbacks(self):
        kwargs = [{**self.frame_kwargs, 'action': int(ids.ActionID.SACK)}, {
            **self.frame_kwargs, 'action': int(ids.ActionID.SNACK)}]
        for element in kwargs:
            callback_key = Frame(**element)
            self._logger.debug(f"Added callback {callback_key}")
            self.cm.unregister_callback(callback_key)
            self.cm.register_callback(self.on_receive, callback_key)
