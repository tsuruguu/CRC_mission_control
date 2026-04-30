from typing import List

from kivy.uix.widget import Widget
from kivymd.app import MDApp
from kivymd.uix.button import BaseButton
from kivymd.uix.dialog import MDDialog


class SpacePopup(MDDialog):

    def __init__(self, title: str, content: Widget, buttons: List[BaseButton], **kwargs) -> None:
        content_type = 'alert' if content is None else 'custom'
        super().__init__(title=title, type=content_type, content_cls=content,
                         buttons=buttons, **kwargs)
        app = MDApp.get_running_app()
        self.md_bg_color = app.theme_cls.bg_light
        self.ids.title.color = app.theme_cls.primary_color
        self.ids.text.color = app.theme_cls.text_color
        if content is not None:
            self.ids.container.size_hint = (1, 1)
            self.ids.spacer_top_box.size_hint = (1, 1)
