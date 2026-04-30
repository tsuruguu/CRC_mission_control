from typing import Callable

from kivy.uix.widget import Widget

from rocket_ground_station.components.buttons import SpaceFlatButton
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.components.popups.space_popup import SpacePopup
from rocket_ground_station.components.space_text_field import SpaceTextField


class EnterText(SpacePopup):

    def __init__(self,
                 prompt: str,
                 on_answer: Callable,
                 initial_text: str = '',
                 halt_popup: bool = False, **kwargs) -> None:
        self._on_answer = on_answer
        self._content = SpaceTextField()
        cancel = SpaceFlatButton(text='CANCEL')
        ok = SpaceFlatButton(text='OK')
        cancel.bind(on_release=self.dismiss)
        ok.bind(on_release=self._on_enter_text)
        super().__init__(title=prompt,
                         content=self._content,
                         buttons=[cancel, ok],
                         size_hint=(0.5, 0.3), **kwargs)

        self._content.text = initial_text
        if not halt_popup:
            self.open()

    def _on_enter_text(self, caller: Widget) -> None:
        if self._content.text:
            self._on_answer(self._content.text)
            self.dismiss()
        else:
            Message(title='Error', message='Please enter some text')
