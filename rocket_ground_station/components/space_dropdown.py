from typing import List
from kivy.properties import ListProperty
from kivy.metrics import dp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.app import MDApp

from rocket_ground_station.components.buttons import SpaceFlatButton


class SpaceDropdown(SpaceFlatButton):
    items = ListProperty()
    icons = ListProperty()

    def __init__(self, items: List[str] = None, icons: List[str] = None, **kwargs) -> None:
        super().__init__(icon='menu-down', **kwargs)
        self.items = [] if items is None else items
        self.icons = [] if icons is None else icons
        self.register_event_type('on_select')
        self.menu = self._create_menu(self.items)

    def on_items(self, caller: 'SpaceDropdown', items) -> None:
        items = [
            {
                'text': text,
                'height': dp(56),
                'viewclass': "OneLineListItem",
                'on_release': lambda x=text: self.dispatch('on_select', x)

            } for text in items
        ]
        self.menu = self._create_menu(items)

    def on_icons(self, caller: 'SpaceDropdown', icons) -> None:
        if len(self.items) == len(icons):
            items = [
                {
                    'text': text,
                    'left_icon': icon,
                    'height': dp(56),
                    'viewclass': "SpaceDropdownItem",
                    'on_release': lambda x=text: self.dispatch('on_select', x)
                } for icon, text in zip(icons, self.items)
        ]
            self.menu = self._create_menu(items)

    def on_select(self, text: str) -> None:
        self.menu.dismiss()

    def _create_menu(self, items):
        app = MDApp.get_running_app()
        if hasattr(self, 'menu') and self.menu is not None:
            self.menu.unbind(on_release=self._on_menu_release)
        menu = MDDropdownMenu(caller=self,
                              theme_cls=app.theme_cls,
                              width_mult=4,
                              items=items,
                              radius=[5, 5, 5, 5],
                              background_color=app.theme_cls.bg_light)
        menu.bind(on_release=self._on_menu_release)
        return menu

    def _on_menu_release(self, menu, menu_item):
        self.dispatch('on_select', menu_item.text)

    def on_release(self):
        self.menu.open()
