from kivy.properties import StringProperty, ObjectProperty

from rocket_ground_station.components.device_widgets import SensorWidget
from rocket_ground_station.components.visuals.visual import Visual


class PressureGauge(Visual):
    """Implements a visual representation of a pressure gauge for HydroVisualisation"""
    placement = StringProperty("top")  # top bottom right left
    icon_center_pos_hint = ObjectProperty((.0, .0))
    round_to = ObjectProperty(None)
    _supported_device_widgets = (SensorWidget,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
