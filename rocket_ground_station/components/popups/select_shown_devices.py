from rocket_ground_station.components.device_selector import DeviceSelector
from rocket_ground_station.components.popups.space_popup import SpacePopup
from rocket_ground_station.components.buttons import SpaceFlatButton
from typing import Set, Tuple, Dict, Callable


class SelectShownDevices(SpacePopup):

    def __init__(self,
                 curr_devices: Dict[str, Tuple[str, int]],
                 shown_devices: Set[Tuple[int, int]],
                 on_close_callback: Callable,
                 **kwargs) -> None:
        abort = SpaceFlatButton(text='CLOSE')
        abort.bind(on_release=self.dismiss)
        self.bind(on_dismiss=self.handle_cleanup)
        self._content = DeviceSelector(curr_devices, shown_devices)
        self.on_close_callback = on_close_callback
        self.shown_devices = shown_devices
        super().__init__(title='Choose devices to display',
                         content=self._content,
                         buttons=[abort],
                         size_hint=(0.8, 0.8), **kwargs)
        self.open()

    def handle_cleanup(self, _instance):
        self._content.cancel_intervals()
        self.on_close_callback(self, self.shown_devices)
