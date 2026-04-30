from kivy.properties import StringProperty, ObjectProperty, NumericProperty

from rocket_ground_station.components.device_widgets import SensorWidget
from rocket_ground_station.components.visuals.visual import Visual


class PistonVisual(Visual):
    """Implements a visual representation of a piston for HydroVisualisation"""
    placement = StringProperty("top")  # top bottom right left
    icon_center_pos_hint = ObjectProperty((.0, .0))
    piston_width = NumericProperty(60)
    _supported_device_widgets = (SensorWidget,)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
