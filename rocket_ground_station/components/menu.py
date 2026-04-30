import logging

from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from rocket_ground_station.core.communication import CommunicationManager
from rocket_ground_station.core.communication.mock_communication_manager import MockCommunicationManager
from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.core.configs import AppConfig
from rocket_ground_station.components.tabs import Tab

from rocket_ground_station.core.communication.proxy_processors import ProxySourcePostProcessor


class Menu(BoxLayout, logging.Handler):
    """
    Implements the main menu and methods for tab management.
    """
    tabs = ObjectProperty()
    action_bar = ObjectProperty()
    connection_button = ObjectProperty()
    log_label = ObjectProperty()
    hardware_label = ObjectProperty()
    arming_buttons = ObjectProperty()
    log_label = ObjectProperty()

    def __init__(self, mock_mode: bool = False, **kwargs) -> None:
        super().__init__(**kwargs)
        self._logger = logging.getLogger('main')
        self._tabs = self._create_tabs(mock_mode)
        self._logger.addHandler(self)
        self._populate_action_bar()
        self._current_tab = None
        self._switch_tab('hardware')
        self._tabs['hardware'].load_hardware_config(AppConfig().default_hardware_config)

    def _create_communication_manager(self,
                                      mock_mode: bool = False) -> CommunicationManager:
        if not mock_mode:
            communication = CommunicationManager()
            communication.register_pattern_post_processor(ProxySourcePostProcessor())
        else:
            communication = MockCommunicationManager()

        return communication

    def _create_tabs(self, mock_mode: bool = False) -> dict:
        """
        Creates tab objects, preserving the dependencies and config order.
        :return: dict with Tab objects with their titles as keys
        """
        communication = self._create_communication_manager(mock_mode)
        tabs = {}
        tabs['logger'] = Tab.from_title('logger', tabs)
        self._logger.addHandler(tabs['logger'])
        tabs['communication'] = Tab.from_title(
            'communication', tabs, cm=communication)
        tabs['hardware'] = Tab.from_title(
            'hardware', tabs, cm=communication)
        for title in AppConfig().tabs:
            if not title in tabs:
                tabs[title] = Tab.from_title(title, tabs)
            self.tabs.add_widget(tabs[title])
        return tabs

    def emit(self, record: logging.LogRecord) -> None:
        self.on_log(LogLevel(record.levelno), record.asctime, record.msg)

    def _populate_action_bar(self):
        self.connection_button.communication_tab = self._tabs['communication']
        self.arming_buttons.hardware_tab = self._tabs['hardware']

    def _switch_tab(self, title, button: Button = None) -> None:
        """
        Hides currently visible tab and shows the requested one. A callback for tab buttons.
        :param title: a title of the tab that becomes visible
        :param button: button instance that called this method
        """
        self.tabs.switch_tab(title.upper(), search_by='title')

    def on_log(self, level: LogLevel, timestamp: str, msg: str):
        self.log_label.text = msg

    def on_close(self) -> None:
        """
        Called just before the application is closed.
        """
        for tab in self._tabs.values():
            tab.on_close()
