from typing import Dict, Callable

from kivy.uix.widget import Widget

from rocket_ground_station.core.sequences import RocketSequence
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.configs import HardwareConfig
from rocket_ground_station.components.buttons import SpaceFlatButton
from rocket_ground_station.components.popups.space_popup import SpacePopup
from rocket_ground_station.components.popups.question import BinaryQuestion
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.components.popups.enter_text import EnterText
from rocket_ground_station.components.sequences import SequenceEditor


class EditSequence(SpacePopup):

    def __init__(self,
                 sequence: RocketSequence,
                 sequences: Dict[str, RocketSequence],
                 devices: Dict[str, Device],
                 config: HardwareConfig,
                 editing_finished_cb: Callable, **kwargs) -> None:
        self._sequences = sequences
        self._config = config
        self._editing_finished_cb = editing_finished_cb
        self._editor = SequenceEditor()
        remove = SpaceFlatButton(text='REMOVE')
        save = SpaceFlatButton(text='SAVE')
        cancel = SpaceFlatButton(text='CANCEL')
        save_as = SpaceFlatButton(text='SAVE AS')
        remove.bind(on_release=self.remove)
        save.bind(on_release=self.save)
        cancel.bind(on_release=self.dismiss)
        save_as.bind(on_release=self.save_as)
        super().__init__(title=f'Editing the {sequence.name} sequence',
                         content=self._editor,
                         buttons=[remove, save, save_as, cancel],
                         size_hint=(0.95, 0.95), **kwargs)
        self._editor.open(sequence, devices)
        self.open()

    def save(self, _caller: Widget, new_name: str = None) -> None:
        if new_name is not None:
            self._editor.set_sequence_name(new_name.replace(' ', '_'))
        edited_sequence = self._editor.as_sequence()
        validation_error_stack = []
        max_validation_result = edited_sequence.check_max_time()
        pair_validation_result, unpaired_operation = edited_sequence.validate_open_close_parity()

        if not max_validation_result:
            validation_error_stack.append('Max time exceeded. Do you want to continue?')
        if not pair_validation_result:
            validation_error_stack.append('Unpaired open/close operation found\n'
                                          'Would you like to continue anyway?\n'
                                          f'unpaired operation: {unpaired_operation}')

        def perform_sequence_save():
            self._sequences[edited_sequence.name] = edited_sequence
            self._update_config()
            self._editing_finished_cb(edited_sequence.name)
            Message(title='Info', message='Sequence has been saved successfully')
            self.dismiss()

        def question_handler(answer):
            if answer:
                validation_error_stack.pop(0)
                handle_validation_errors()

        def handle_validation_errors():
            if len(validation_error_stack) > 0:
                BinaryQuestion(question=validation_error_stack[0],
                               on_answer=question_handler)
            else:
                perform_sequence_save()

        handle_validation_errors()

    def remove(self, caller: Widget) -> None:
        def on_answer(remove: bool):
            if remove:
                edited_sequence = self._editor.as_sequence()
                if edited_sequence.name in self._sequences:
                    del self._sequences[edited_sequence.name]
                self._update_config()
                self._editing_finished_cb(None)
                Message(title='Info', message='Sequence has been removed successfully')
                self.dismiss()

        BinaryQuestion('Are you sure you want to remove this sequence?', on_answer)

    def save_as(self, _caller: Widget):
        def on_answer_name(new_name: str):
            self.save(self, new_name)

        old_name = self._editor.as_sequence().name
        message = ('Please enter new sequence name, '
                   'be careful to not overwrite any other existing sequence when choosing the name!')
        EnterText(message,
                  on_answer_name,
                  initial_text=old_name)

    def _update_config(self) -> None:
        sequences = {seq.name: [op.as_dict() for op in seq] for seq in self._sequences.values()}
        self._config.update('sequences', sequences)
        self._config.save()
