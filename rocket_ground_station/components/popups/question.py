from functools import partial
from typing import Callable, Iterable

from rocket_ground_station.components.buttons import SpaceFlatButton
from rocket_ground_station.components.popups.space_popup import SpacePopup


class Question(SpacePopup):
    """
    Implements a popup which displays a question and calls given callback with the answer.
    """

    def __init__(self, question: str, on_answer: Callable, answers: Iterable[str],
                 halt_popup: bool = False, **kwargs):
        """
        :param question: text that will be displayed as a title of the popup
        :param answers: list of possible answers
        :param on_answer: function that will be called with the answer
        :param halt_popup: if True, the popup doesn't show after it is created
        """
        buttons = [SpaceFlatButton(text=ans) for ans in answers]
        for button in buttons:
            button.bind(on_release=self.on_answer)
        super().__init__(title=question, content=None, buttons=buttons, **kwargs)
        self.user_callback = on_answer
        self.auto_dismiss = False
        if not halt_popup:
            self.open()

    def on_answer(self, button: SpaceFlatButton) -> None:
        self.on_dismiss = partial(self.user_callback, button.text)
        self.dismiss()


class BinaryQuestion(Question):
    """
    Wrapper for questions to which the answer is boolean.
    """

    def __init__(self, question: str, on_answer: Callable, answers: Iterable[str] = None,
                 halt_popup: bool = False, **kwargs):
        answers = ('NO', 'YES') if answers is None else answers
        super().__init__(question, on_answer, answers, halt_popup, **kwargs)
        self.true_answer = self.buttons[-1].text

    def on_answer(self, button: SpaceFlatButton) -> None:
        self.on_dismiss = partial(self.user_callback, button.text == self.true_answer)
        self.dismiss()
