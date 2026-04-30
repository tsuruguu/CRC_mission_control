from typing import List
from functools import partial
import time

from kivy.properties import ObjectProperty, DictProperty, NumericProperty, StringProperty
from kivy.clock import Clock

from rocket_ground_station.core.devices import Scheduler
from rocket_ground_station.core.communication import Frame
from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.components.device_widgets.device_widget import DeviceWidget
from rocket_ground_station.components.popups.question import BinaryQuestion


class SchedulerWidget(DeviceWidget):
    frames_left = NumericProperty(0)
    expect_acks_from = ObjectProperty([])
    ack_states = DictProperty({
        'START': AckStatus.READY,
        'CLEAR': AckStatus.READY,
        'ABORT': AckStatus.READY
    })

    # Sequence tracking properties
    is_sequence_running = ObjectProperty(False)
    current_sequence = ObjectProperty(None, allownone=True)
    sequence_start_time = NumericProperty(0)
    next_operation_text = StringProperty("Sequence State Unknown")
    time_to_next_operation = StringProperty("")
    current_sequence_name = StringProperty("")

    def __init__(self, device: Scheduler):
        super().__init__(device)
        self.close_on_finish = self._device.close_on_finish
        self.expect_acks_from = self._device.expect_acks_from
        self.acks_left = 0
        self._update_event = None
        self._current_operation_index = 0

        self.register_event_type('on_start')
        self.register_event_type('on_clear')
        self.register_event_type('on_abort')
        self.register_event_type('on_frame_uploaded')

    def start(self) -> None:
        def on_launch(launch: bool) -> None:
            if launch:
                self.reset_ack_states()
                self.ack_states['START'] = AckStatus.WAITING
                self.acks_left = len(self.expect_acks_from)
                self._device.start(partial(self.dispatch, 'on_start'))
        BinaryQuestion('Are you sure you want to start the sequence?', on_launch)

    def on_start(self, ack: bool) -> None:
        self._verify_remaining_acks(ack, 'START')
        if ack and self.current_sequence:
            self._start_sequence_tracking()

    def clear(self) -> None:
        self.reset_ack_states()
        self.ack_states['CLEAR'] = AckStatus.WAITING
        self.acks_left = len(self.expect_acks_from)
        self._device.clear(partial(self.dispatch, 'on_clear'))

    def on_clear(self, ack: bool) -> None:
        self._verify_remaining_acks(ack, 'CLEAR')
        if ack:
            # Fully clear sequence tracking on clear
            self.is_sequence_running = False
            if self._update_event:
                self._update_event.cancel()
                self._update_event = None
            self.current_sequence = None
            self.current_sequence_name = ""
            self._current_operation_index = 0
            self.next_operation_text = "No Sequence Uploaded"
            self.time_to_next_operation = ""

    def abort(self) -> None:
        self.reset_ack_states()
        self.ack_states['ABORT'] = AckStatus.WAITING
        self.acks_left = len(self.expect_acks_from)
        self._device.abort(partial(self.dispatch, 'on_abort'))

    def on_abort(self, ack: bool) -> None:
        self._verify_remaining_acks(ack, 'ABORT')
        if ack:
            # Stop sequence tracking and show aborted message
            self.is_sequence_running = False
            if self._update_event:
                self._update_event.cancel()
                self._update_event = None
            self._current_operation_index = 0
            self.next_operation_text = "Sequence Aborted"
            self.time_to_next_operation = ""

    def _verify_remaining_acks(self, ack: bool, ack_state_name: str):
        if ack:
            self.acks_left -= 1
        else:
            self.ack_states[ack_state_name] = AckStatus.FAILED
        if self.acks_left == 0:
            self.ack_states[ack_state_name] = AckStatus.SUCCESSFUL

    def upload_sequence(self, sequence: List[Frame]) -> None:
        self.clear()
        self.frames_left = len(sequence)
        # Store the frames for upload, but keep operations for tracking
        # (the operations for tracking are set separately via set_current_sequence_for_tracking)
        self._device.upload_sequence(sequence, partial(self.dispatch, 'on_frame_uploaded'))

    def on_frame_uploaded(self, frame: Frame, ack: bool, frames_left: int) -> None:
        self.frames_left = frames_left

    def terminate_sequence_upload(self) -> None:
        self._device.terminate_sequence_upload()
        # Fully clear sequence tracking on termination
        self.is_sequence_running = False
        if self._update_event:
            self._update_event.cancel()
            self._update_event = None
        self.current_sequence = None
        self.current_sequence_name = ""
        self._current_operation_index = 0
        self.next_operation_text = "No Sequence Uploaded"
        self.time_to_next_operation = ""

    def set_current_sequence_for_tracking(self, sequence_operations, sequence_name=""):
        """Set the current sequence operations for tracking purposes - only after sequence upload"""
        if sequence_operations is None:
            self.current_sequence = None
            self.current_sequence_name = ""
            self._current_operation_index = 0
            self.next_operation_text = "No Sequence Uploaded"
            self.time_to_next_operation = ""
            return

        self.current_sequence = sequence_operations
        self.current_sequence_name = sequence_name
        self._current_operation_index = 0
        # Show sequence name after upload
        if not self.is_sequence_running:
            self.next_operation_text = f"Sequence: {sequence_name}" if sequence_name else "Sequence Uploaded"
            self.time_to_next_operation = "Ready to start"

    def _start_sequence_tracking(self):
        """Start tracking the sequence execution"""
        if not self.current_sequence:
            return

        self.is_sequence_running = True
        self.sequence_start_time = time.time()
        self._current_operation_index = 0

        # Start periodic updates
        self._update_event = Clock.schedule_interval(self._update_sequence_display, 0.1)
        self._update_sequence_display(0)

    def _stop_sequence_tracking(self):
        """Stop tracking the sequence execution"""
        self.is_sequence_running = False
        if self._update_event:
            self._update_event.cancel()
            self._update_event = None
        # Don't clear the sequence here - we'll keep it to show "SEQUENCE FINISHED"
        self._current_operation_index = 0

    def _update_sequence_display(self, dt):
        """Update the display showing next operation and time remaining"""
        if not self.is_sequence_running or not self.current_sequence:
            return False

        current_time = time.time() - self.sequence_start_time
        current_time_ms = int(current_time * 1000)

        # Find the next operation that hasn't been executed yet
        cumulative_time = 0
        next_operation = None
        time_to_next = 0

        for i, operation in enumerate(self.current_sequence):
            cumulative_time += operation.starts_after
            if cumulative_time > current_time_ms:
                next_operation = operation
                time_to_next = cumulative_time - current_time_ms
                self._current_operation_index = i
                break

        if next_operation:
            # Format the next operation text
            self.next_operation_text = f"{next_operation.device_name}: {next_operation.operation.upper()}"

            # Format time remaining
            seconds_remaining = time_to_next / 1000.0
            if seconds_remaining >= 60:
                minutes = int(seconds_remaining // 60)
                seconds = seconds_remaining % 60
                self.time_to_next_operation = f"{minutes}m {seconds:.1f}s"
            else:
                self.time_to_next_operation = f"{seconds_remaining:.1f}s"
        else:
            # Sequence finished
            self.next_operation_text = "SEQUENCE FINISHED"
            self.time_to_next_operation = ""
            self._stop_sequence_tracking()
            return False  # Stop the update loop

        return True
