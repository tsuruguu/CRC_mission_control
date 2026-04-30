import logging
from typing import Dict

from kivy.properties import DictProperty, ObjectProperty, StringProperty

from rocket_ground_station.core.sequences import RocketSequence
from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.core.configs import HardwareConfig
from rocket_ground_station.components.device_widgets import DeviceWidget, SchedulerWidget
from rocket_ground_station.components.popups import Message, BinaryQuestion
from rocket_ground_station.components.sequences import SequenceDisplayer
from rocket_ground_station.components.tabs.tab import Tab
from rocket_ground_station.components.popups import UploadSequence, EditSequence, EnterText


class Sequences(Tab):
    sequences = DictProperty({})
    current_sequence_name = StringProperty('')
    last_uploaded_sequence_name = StringProperty('')
    sequence_displayer: SequenceDisplayer = ObjectProperty()

    def __init__(self, **tab_kwargs) -> None:
        super().__init__(**tab_kwargs)
        self._hardware_config = None
        self._sequences_logger = logging.getLogger('sequences')
        self._logger.info('Sequences tab initialized')

    def on_successful_upload(self, caller):
        self.last_uploaded_sequence_name = self.current_sequence_name
        self._sequences_logger.info(f'Sequence uploaded successfully: {self.last_uploaded_sequence_name}')

        # Set the sequence operations for tracking after successful upload
        scheduler = self._get_scheduler(self._device_widgets)
        if scheduler is not None:
            sequence_operations = self.sequences[self.current_sequence_name].operations
            scheduler.set_current_sequence_for_tracking(sequence_operations, self.current_sequence_name)

    def on_clear(self, _caller, _value):
        self._sequences_logger.info('Sent scheduler clear, no sequence is currently loaded on hardware')
        self.last_uploaded_sequence_name = ''
        # Also clear the sequence tracking in the scheduler widget
        scheduler = self._get_scheduler(self._device_widgets)
        if scheduler is not None:
            scheduler.set_current_sequence_for_tracking(None, "")

    def on_start(self, _caller, _value):
        if not self.last_uploaded_sequence_name:
            self._sequences_logger.warning(
                'Sent scheduler start but no sequence was uploaded after clearing scheduler')
            self._sequences_logger.warning('Unexpected things may happen!')
            return

        if self.last_uploaded_sequence_name not in self.sequences.keys():
            self._sequences_logger.warning(
                f'Sent scheduler start but last uploaded sequence "{self.last_uploaded_sequence_name}" '
                f'is not present in current HW config')
            self._sequences_logger.warning('Unexpected things may happen!')
            self._sequences_logger.warning('Unable to print sequence since no operation data is available')
            return

        self._sequences_logger.info(f'Starting sequence: {self.last_uploaded_sequence_name}')
        self._sequences_logger.info(f'{"Device Type":15s}'
                                    f'{"Device name":15s}'
                                    f'{"Operation":18s}'
                                    f'{"Starts after":20s}'
                                    f'{"Payload":20s}')
        for operation in self.sequences[self.last_uploaded_sequence_name].operations:
            self._sequences_logger.info(f'{operation.device_type:15s}'
                                        f'{operation.device_name:15s}'
                                        f'{operation.operation:15s}'
                                        f'{operation.starts_after:15d}'
                                        f'{operation.payload:15d}')

    def on_hardware_load(self, device_widgets: Dict[str, DeviceWidget], hardware_config: HardwareConfig
                         ) -> None:
        self._hardware_config = hardware_config
        self._device_widgets = device_widgets
        self.sequences = self._create_valid_sequences(device_widgets)
        self.display_sequence()
        _scheduler = self._get_scheduler(device_widgets)
        _scheduler.bind(on_start=self.on_start)
        _scheduler.bind(on_clear=self.on_clear)

    def _create_valid_sequences(self, device_widgets: Dict[str, DeviceWidget]
                                ) -> Dict[str, RocketSequence]:
        sequences = {name: RocketSequence.from_config(name, config) for
                     name, config in self._hardware_config.sequences.items()}
        devices = {name: d_w.as_device() for name, d_w in device_widgets.items()}
        return {name: seq for name, seq in sequences.items() if seq.validate(devices)}

    def display_sequence(self, sequence_name: str = None) -> None:
        if sequence_name is not None:
            sequence = self.sequences.get(sequence_name, None)
        elif self.sequences:
            sequence = next(iter(self.sequences.values()))
        else:
            sequence = None
        self.sequence_displayer.display(sequence)
        self.current_sequence_name = sequence.name if sequence is not None else ''

    def upload_sequence(self) -> None:
        if not self._tabs['communication'].is_connected:
            msg = 'Cannot send the sequence when connection with a rocket is closed'
            self._logger.error(f'Connection error: {msg}')
            Message.create(LogLevel.ERROR, msg)
            return
        scheduler = self._get_scheduler(self._device_widgets)
        if scheduler is None:
            msg = 'Cannot send the sequence when there is no scheduler in hardware config'
            self._logger.error(f'Scheduler error: {msg}')
            Message.create(LogLevel.ERROR, msg)
            return
        if not scheduler.is_device_armed:
            msg = 'Cannot send the sequence when the hardware is not armed'
            self._logger.error(f'Logic error: {msg}')
            Message.create(LogLevel.ERROR, msg)
            return

        validation_error_stack = []
        pair_validation_result, unpaired_operation = self.sequences[self.current_sequence_name] \
            .validate_open_close_parity()
        max_validation_result = self.sequences[self.current_sequence_name].check_max_time()

        if not max_validation_result:
            validation_error_stack.append('Max time exceeded. Do you want to continue?')
        if not pair_validation_result:
            validation_error_stack.append('Unpaired open/close operation found\n'
                                          'Would you like to continue anyway?\n'
                                          f'unpaired operation: {unpaired_operation}')

        def perform_sequence_upload():
            devices = {name: d_w.as_device() for name, d_w in self._device_widgets.items()}
            UploadSequence(self.current_sequence_name,
                           self.sequences[self.current_sequence_name].as_frames(devices),
                           scheduler).bind(on_successful_upload=self.on_successful_upload)

        def question_handler(answer):
            if answer:
                validation_error_stack.pop(0)
                handle_validation_errors()

        def handle_validation_errors():
            if len(validation_error_stack) > 0:
                BinaryQuestion(question=validation_error_stack[0],
                               on_answer=question_handler)
            else:
                perform_sequence_upload()

        handle_validation_errors()

    @staticmethod
    def _get_scheduler(device_widgets: Dict[str, DeviceWidget]) -> SchedulerWidget:
        schedulers = [device_widget for device_widget in device_widgets.values()
                      if isinstance(device_widget, SchedulerWidget)]
        return schedulers[0] if len(schedulers) > 0 else None

    def edit_sequence(self, sequence_name: str) -> None:
        devices = {name: d_w.as_device() for name, d_w in self._device_widgets.items()}
        sequence = self.sequences.get(sequence_name, RocketSequence(sequence_name))
        EditSequence(sequence, self.sequences, devices, self._hardware_config, self.display_sequence)

    def new_sequence(self) -> None:
        def on_answer(name: str):
            self.edit_sequence(name.replace(' ', '_'))

        EnterText('Enter the new sequence name', on_answer)

    def abort_sequence(self) -> None:
        scheduler = self._get_scheduler(self._device_widgets)
        if scheduler is not None:
            scheduler.abort()
