from os.path import dirname
from typing import Dict, List
import logging
from pathlib import Path

from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.tab import MDTabsBase

from rocket_ground_station.core.exceptions import TabNotImplementedError


class Tab(BoxLayout, MDTabsBase):
    """
    Implements a generic Tab used for displaying content in the main window of ground station.
    """
    implemented_tabs = {}

    def __init_subclass__(cls) -> None:
        """
        Registers the new type of tab and loads its kv gui file every time Tab is subclassed.
        """
        super().__init_subclass__()
        cls.title = cls.__name__.lower()
        Tab.implemented_tabs[cls.title] = cls

        kv_filename = cls.title + '.kv'
        path = Path(dirname(__file__)).resolve()
        kv_path = None
        while True:
            candidate = path.joinpath('layouts', 'tabs', kv_filename)
            if candidate.is_file():
                kv_path = str(candidate)
                break
            if path == path.parent:
                break
            path = path.parent
        if kv_path is None:
            raise FileNotFoundError(f'Could not find kv file for tab: {kv_filename}')
        Builder.load_file(kv_path)

    def __init__(self, tabs: dict, **kwargs) -> None:
        """
        :param tabs: a dict with all Tab objects used currently in app
        """
        self._logger = logging.getLogger('main')
        self._tabs: Dict[str, 'Tab'] = tabs
        self.tab_label_font_style = 'SpaceTitleLabel'
        super().__init__(title=self.title.upper(), **kwargs)
        self._device_widgets = {}

    @staticmethod
    def from_title(title: str, tabs: dict, **kwargs):
        """
        Creates new tab based on a title (fails if a tab of such title was not implemented).
        :param title: a key uniquely representing a tab class in implemented_tabs dict
        :param tabs: a dict with all Tab objects used currently in app
        :return: new Tab instance of the given title
        """
        try:
            return Tab.implemented_tabs[title](tabs=tabs, **kwargs)
        except KeyError:
            raise TabNotImplementedError(f'Failed to create a tab with title: {title}')

    @staticmethod
    def _populate_dropdown(items: List[str], dropdown_widget: Widget, icon: str) -> None:
        dropdown_widget.items = items
        icons = [icon]*len(items)
        dropdown_widget.icons = icons

    def on_hide(self) -> None:
        """
        Called when this Tab is hidden by the user. Default implementation does nothing.
        """

    def on_show(self) -> None:
        """
        Called when this Tab is clicked by the user. Default implementation does nothing.
        """

    def on_close(self) -> None:
        """
        Called just before the application is closed. Default implementation does nothing.
        """

    @property
    def app(self) -> MDApp:
        return MDApp.get_running_app()
