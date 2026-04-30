from kivy.properties import StringProperty, ObjectProperty, AliasProperty
from kivymd.uix.floatlayout import MDFloatLayout


class Visual(MDFloatLayout):
    """Visual representation of device widgets for hydro visualization"""
    name = StringProperty()
    _device_widget = ObjectProperty(rebind=True, allownone=True)
    _supported_device_widgets = tuple()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def supported_device_widgets(self):
        return type(self)._supported_device_widgets

    def get_device_widget(self):
        return self._device_widget

    def set_device_widget(self, value):
        if not isinstance(value, self.supported_device_widgets + (type(None),)):
            raise ValueError(f"{type(value)} not supported by {type(self)} Visual. "
                             f"Supported types: {self.supported_device_widgets}")
        self._device_widget = value

    device_widget = AliasProperty(get_device_widget, set_device_widget,
                                  bind=['_device_widget'], rebind=True, allownone=True)
