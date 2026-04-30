import logging
from typing import List

from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.communication import Frame
from rocket_ground_station.components.buttons import SpaceFlatButton
from rocket_ground_station.components.popups.space_popup import SpacePopup
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.components.device_widgets import SchedulerWidget
from rocket_ground_station.core.communication.ids import LogLevel


class UploadSequence(SpacePopup):

    def __init__(self,
                 name: str,
                 sequence: List[Frame],
                 scheduler_widget: SchedulerWidget,
                 **kwargs) -> None:
        self._logger = logging.getLogger('main')
        self._seqence = list(sequence)
        self._scheduler_widget = scheduler_widget
        self.register_event_type('on_successful_upload')
        abort = SpaceFlatButton(text='CANCEL')
        abort.bind(on_release=self.dismiss)
        scheduler_widget.bind(on_frame_uploaded=self.on_frame_uploaded)
        self._content = UploadSequenceContent(sequence, scheduler_widget)
        super().__init__(title=f'Sending the {name} sequence',
                         content=self._content,
                         buttons=[abort],
                         size_hint=(0.8, 0.4), **kwargs)
        self.open()
        scheduler_widget.upload_sequence(sequence)

    def on_frame_uploaded(self, caller: Widget, frame: Frame, ack: bool, frames_left: int) -> None:
        if not frames_left:
            self.dismiss()

    def on_successful_upload(self):
        pass

    def on_dismiss(self) -> None:
        self._scheduler_widget.unbind(on_frame_uploaded=self.on_frame_uploaded)
        if self._scheduler_widget.frames_left - 1:
            self._scheduler_widget.terminate_sequence_upload()
            self._logger.warning('Sequence upload has been terminated')
            Message.create(LogLevel.WARNING, 'Sequence upload has been terminated')
        elif not all(self._content.acknowledgements):
            failed_frames = [str(frame) for ack, frame in
                             zip(self._content.acknowledgements, self._seqence)
                             if not ack]
            msg = 'Frames:\n' + \
                  '\n'.join(failed_frames) + '\nhave not been acknowledged'
            self._logger.error(msg)
            Message.create(LogLevel.ERROR, msg)
        else:
            self._logger.info('Sequence has been uploaded successfully')
            Message.create(LogLevel.INFO, 'Sequence has been uploaded successfully')
            self.dispatch('on_successful_upload')
        self.unregister_event_type('on_successful_upload')


class UploadSequenceContent(MDBoxLayout):
    upload_bar = ObjectProperty()
    operation_label = ObjectProperty()
    frame_count_label = ObjectProperty()

    def __init__(self, sequence: List[Frame], scheduler_widget: SchedulerWidget, **kwargs) -> None:
        super().__init__(**kwargs)
        self._seqence = sequence
        self._scheduler_widget = scheduler_widget
        self._acknowledgements = [False] * len(self._seqence)
        self.frame_count_label.text = f'(0/{len(self._seqence)})'
        self.operation_label.text = 'Sending: ' + str(self._seqence[0])
        scheduler_widget.bind(on_frame_uploaded=self.on_frame_uploaded)

    def on_frame_uploaded(self, caller: Widget, frame: Frame, ack: bool, frames_left: int) -> None:
        frames_sent = len(self._seqence) - frames_left
        self._acknowledgements[frames_sent - 1] = ack
        self.upload_bar.value = 100 * frames_sent / len(self._seqence)
        self.frame_count_label.text = f'({frames_sent}/{len(self._seqence)})'
        if frames_left:
            self.operation_label.text = 'Sending: ' + \
                                        str(self._seqence[frames_sent])
        else:
            self._scheduler_widget.unbind(
                on_frame_uploaded=self.on_frame_uploaded)

    @property
    def acknowledgements(self) -> List[bool]:
        return self._acknowledgements
