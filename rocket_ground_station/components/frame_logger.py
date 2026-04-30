from datetime import datetime
from typing import Dict, Tuple, Set
from pathlib import Path
import sys

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty, BooleanProperty, DictProperty
from kivymd.uix.boxlayout import MDBoxLayout

from rocket_ground_station.core.communication import Frame
from rocket_ground_station.core.communication.ids import ActionID, DeviceID
from rocket_ground_station.components.popups import SelectShownDevices


class FrameLogger(MDBoxLayout):
    logs = ObjectProperty()
    log_services = BooleanProperty(True)
    log_requests = BooleanProperty(True)
    log_schedules = BooleanProperty(True)
    log_feeds = BooleanProperty(False)
    hardware = ObjectProperty()
    current_devices = DictProperty()
    shown_devices = ObjectProperty()
    shown_device_types = ObjectProperty(defaultvalue={})
    shown_device_ids = ObjectProperty(defaultvalue={})

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._feed_actions = (int(ActionID.FEED),)
        self._service_actions = (int(ActionID.SERVICE), int(ActionID.ACK), int(ActionID.NACK),
                                 int(ActionID.HEARTBEAT))
        self._schedule_actions = (int(ActionID.SCHEDULE), int(ActionID.SACK), int(ActionID.SNACK))
        self._request_actions = (int(ActionID.REQUEST), int(ActionID.RESPONSE))
        self.log_file = None
        self._logs_to_write = []
        self._fonts_size = App.get_running_app().theme_cls.font_styles['FrameLogger'][1]

    def log_frame(self, frame: Frame, received: bool, error: bool = False) -> None:
        max_line = (10000, 9500)
        arrow = 'd' if received else 'u'
        timestamp = datetime.now().strftime('%H_%M_%S_%f')
        log = ' '.join((arrow, timestamp, str(frame), '\n'))
        self._logs_to_write.append(log)

        if not self.filter_by_shown(frame):
            return

        if not self.filter_log_level(frame.action):
            return

        frame = frame.as_mono_str()
        frame = f'[color=e0525c][b]{frame}[/b][/color]' if error else frame
        timestamp = f'[color=878a8c][{timestamp}][/color]'
        log = (f'{arrow} [size={self._fonts_size}dp][font=RobotoMono-Regular] '
               f'{timestamp} {frame} [/font][/size] \n')
        self.logs.text = log + self.logs.text
        if len(self.logs.text) > max_line[0]:
            next_line = self.logs.text.find('\n', max_line[1])
            self.logs.text = self.logs.text[:next_line]

    def filter_by_shown(self, frame: Frame) -> bool:

        special_devices = (int(DeviceID.KEEPALIVE),)

        if frame.device_type in special_devices:
            return True

        if frame.device_type not in self.shown_device_types:
            return False

        if frame.device_id not in self.shown_device_ids:
            return False

        return True

    def filter_log_level(self, action) -> bool:
        if action in self._feed_actions and self.log_feeds:
            return True
        if action in self._service_actions and self.log_services:
            return True
        if action in self._schedule_actions and self.log_schedules:
            return True
        if action in self._request_actions and self.log_requests:
            return True
        return False

    def on_shown_devices(self, _caller: Widget, shown_devices: Set[Tuple[int, int]]):
        self.shown_device_types = {pair[0] for pair in shown_devices}
        self.shown_device_ids = {pair[1] for pair in shown_devices}

    def on_current_devices(self, _caller: Widget, devices_to_display: Dict[str, Tuple[str, int]]):
        self.shown_devices = {(DeviceID[d_name.upper()].value, d_id)
                              for d_name, d_id in
                              devices_to_display.values()}

    def filter(self) -> None:
        SelectShownDevices(self.current_devices, self.shown_devices, on_close_callback=self.on_shown_devices)

    def init_file(self, dt):
        timestamp = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
        log_file_path = Path(sys.argv[0]).resolve().parent.joinpath('logs/frames')
        Path(log_file_path).mkdir(parents=True, exist_ok=True)
        self.log_file = open(Path(log_file_path, timestamp + '_frames.log'), 'w')
        Clock.schedule_interval(self.save_file, dt)

    def save_file(self, dt: float = 5):
        if self._logs_to_write:
            self.log_file.writelines(self._logs_to_write)
            self.log_file.flush()
            self._logs_to_write.clear()

    def close_file(self):
        if self.log_file:
            self.save_file()
            Clock.unschedule(self.save_file)
            self.log_file.close()

    def clear(self):
        self.logs.text = ''
