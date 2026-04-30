from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.components.buttons import SpaceFlatButton
from rocket_ground_station.components.popups.space_popup import SpacePopup


class Message(SpacePopup):
    """
    Implements a default popup window for displaying errors to the user.
    """

    def __init__(self, title: str, message: str, button_text: str = None,
                 halt_popup: bool = False, **kwargs) -> None:
        """
        :param title: the title of the popup window
        :param message: message for the user to display
        :param button_text: text displayed on the popup-closing button
        :param halt_popup: if True, the popup doesn't show after it is created
        """
        buttons = [SpaceFlatButton(text=button_text or 'OK')]
        buttons[0].bind(on_release=self.dismiss)
        super().__init__(title=title, content=None, buttons=buttons, text=message, **kwargs)
        if not halt_popup:
            self.open()

    @staticmethod
    def create(loglevel: LogLevel, message: str):
        Message(title=loglevel.name, message=message)
