from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.tooltip import MDTooltip
from kivymd.uix.boxlayout import MDBoxLayout


class SpaceTooltip(MDTooltip, MDBoxLayout):
    tooltip_text = StringProperty("")
    _mouse_inside = BooleanProperty(False)

    def on_tooltip_text(self, _, value: str) -> None:
        # A hack to update the tooltip text while the tooltip is open
        if self._mouse_inside and self._tooltip:
            label = None
            if self._tooltip.children:
                label = self._tooltip.children[0]
            if label:
                label.text = value

    def on_enter(self, *args) -> None:
        self._mouse_inside = True
        super().on_enter()

    def on_leave(self, *args) -> None:
        self._mouse_inside = False
        super().on_leave()
