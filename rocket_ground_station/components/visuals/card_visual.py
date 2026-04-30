from copy import copy

from kivy.properties import ObjectProperty, AliasProperty, DictProperty, BooleanProperty

from rocket_ground_station.components.device_cards import DeviceCard
from rocket_ground_station.components.visuals.visual import Visual


class CardVisual(Visual):
    """Implements a visual representation of a pressure gauge for HydroVisualisation"""
    icon_center_pos_hint = ObjectProperty((.0, .0))
    device_card = ObjectProperty(rebind=True, allownone=True)
    content = ObjectProperty(rebind=True)
    tabs = DictProperty()
    resize = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.target_pos = copy(self.pos)

    def set_device_widget(self, value):
        self._device_widget = value
        self.content.clear_widgets()

        if value is None:
            return
        # Card scaling is set to 1 since it's irrelevant in the layout setup used by Hydraulics tab
        self.device_card = DeviceCard(self._device_widget, self.tabs['communication'], 1)
        self.content.add_widget(self.device_card)
        self.device_card.pos = self.pos
        self.device_card.pos = self.target_pos
        if self.resize:
            self.device_card.size_hint = (1,1)

    device_widget = AliasProperty(Visual.get_device_widget, set_device_widget,
                                  bind=['_device_widget'], rebind=True, allownone=True)
