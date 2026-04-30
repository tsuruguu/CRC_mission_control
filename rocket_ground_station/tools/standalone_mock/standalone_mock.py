import random
import sys
import time

import os
from os.path import dirname, join, abspath
import threading
from functools import partial
from dataclasses import dataclass
from rocket_ground_station.core.configs import HardwareConfig
from rocket_ground_station.core.communication import ids, Frame
from rocket_ground_station.core.communication import CommunicationManager, TransportType
from rocket_ground_station.core.communication.transport import TransportSettings
from rocket_ground_station.core.communication.exceptions import UnregisteredCallbackError

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.exceptions import TransportTimeoutError # pylint: disable=import-error
    from python_sw_core.communication.tcp_transport import TcpSettings        # pylint: disable=import-error
else:
    from rocket_ground_station.core.communication.exceptions import TransportTimeoutError # pylint: disable=ungrouped-imports
    from rocket_ground_station.core.communication.tcp_transport import TcpSettings        # pylint: disable=ungrouped-imports

from rocket_ground_station.core.communication.serial_transport import SerialSettings
from rocket_ground_station.core.communication.serial_transport import SerialOptions

from pathlib import Path
from datetime import datetime

import logging

from kivymd.app import MDApp
from kivy.core.text import LabelBase
from kivy.properties import ObjectProperty, ListProperty
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window


class TransportColumnContent(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'

    def pack_settings(self) -> TransportSettings:
        raise NotImplementedError


class TcpColumnContent(TransportColumnContent):
    proxy_address = ObjectProperty(None)
    proxy_port = ObjectProperty(None)

    def pack_settings(self) -> TransportSettings:
        address = self.proxy_address.text
        port = int(self.proxy_port.text)
        return TcpSettings(address, port)


class SerialColumnContent(TransportColumnContent):
    port_dropdown = ObjectProperty(None)
    baud_dropdown = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._populate_dropdowns()
        self.port_dropdown.bind(on_select=self._select_port)
        self.baud_dropdown.bind(on_select=self._select_baud)

    def _populate_dropdowns(self):
        options = SerialOptions()
        self.port_dropdown.items = sorted(options.port)
        self.baud_dropdown.items = [str(baud) for baud in sorted(options.baudrate, reverse=True)]
        self.port_dropdown.text = self.port_dropdown.items[0]
        self.baud_dropdown.text = self.baud_dropdown.items[0]

    def pack_settings(self) -> TransportSettings:
        port = self.port_dropdown.text
        baudrate = int(self.baud_dropdown.text)
        return SerialSettings(port, baudrate)

    def _select_port(self, instance, value):
        instance.text = value

    def _select_baud(self, instance, value):
        instance.text = value


@dataclass
class MockSettings:
    transport_settings: TransportSettings
    hardware_config_name: str
    feed_interval: float
    no_print: bool


class StandaloneMockUI(MDApp):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.load_fonts('space', 1.0)
        self.apply_material_theming(True)

    def build(self):
        Builder.load_file('standalone_mock.kv')
        self.mock = StandaloneMock()
        return MainScreen(self.mock)

    def apply_material_theming(self, dark_mode: bool) -> None:
        self.theme_cls.primary_palette = 'Teal'
        if dark_mode:
            self.theme_cls.theme_style = 'Dark'
            # fix for wrong colors defined in kivymd
            self.theme_cls.colors["Dark"] = {
                "StatusBar": "000000",  # bg_darkest
                "AppBar": "181818",  # bg_dark
                "Background": "1f1f1f",  # bg_normal
                "CardsDialogs": "262626",  # bg_light
                "FlatButtonDown": "999999",
            }
        else:
            # TODO: verify light theme
            self.theme_cls.theme_style = 'Light'

    def load_fonts(self, font_name: str, font_scaling: float) -> dict:
        font_dir = abspath(join(dirname(__file__), os.pardir, os.pardir, "assets", "fonts"))
        LabelBase.register(
            name=f"{font_name}_regular",
            fn_regular=join(font_dir, f'{font_name}_regular.ttf'),
        )
        LabelBase.register(
            name=f"{font_name}_bold",
            fn_regular=join(font_dir, f'{font_name}_bold.ttf'),
        )
        LabelBase.register(
            name=f"{font_name}_italic",
            fn_regular=join(font_dir, f'{font_name}_italic.ttf'),
        )
        LabelBase.register(
            name=f"{font_name}_light",
            fn_regular=join(font_dir, f'{font_name}_light.ttf'),
        )
        LabelBase.register(
            name='RobotoMono_regular',
            fn_regular=join(font_dir, 'RobotoMono-Regular.ttf'),
        )
        self.theme_cls.font_styles = {
            'SpaceLabel': ['space_bold', round(18 * font_scaling), False, 0.30],
            'SpaceTitleLabel': ['space_bold', round(24 * font_scaling), False, 0.15],
            'SpaceTipLabel': ['space_bold', round(18 * font_scaling), False, 0.30],
            'SpaceTableHeaderLabel': ['space_bold', round(20 * font_scaling), False, 0.30],
            'H1': ['space_regular', round(96 * font_scaling), False, -1.5],
            'H2': ['space_regular', round(60 * font_scaling), False, -0.5],
            'H3': ['space_bold', round(48 * font_scaling), False, 0],
            'H4': ['space_bold', round(34 * font_scaling), False, 0.25],
            'H5': ['space_bold', round(24 * font_scaling), False, 0],
            'H6': ['space_bold', round(20 * font_scaling), False, 0.15],
            'Subtitle1': ['space_bold', round(16 * font_scaling), False, 0.15],
            'Subtitle2': ['space_bold', round(14 * font_scaling), False, 0.1],
            'Body1': ['space_bold', round(16 * font_scaling), False, 0.5],
            'Body2': ['space_bold', round(14 * font_scaling), False, 0.25],
            'Button': ['space_bold', round(16 * font_scaling), True, 1.5],
            'Caption': ['space_bold', round(12 * font_scaling), False, 0.4],
            'Overline': ['space_bold', round(10 * font_scaling), True, 1.5],
            'Icon': ['Icons', round(24 * font_scaling), False, 0],
            'FrameLogger': ['RobotoMono_regular',
                            round(17 * font_scaling * (1.15 if font_scaling < 1 else 1)),
                            False, 0],
        }

        return {'regular': join(font_dir, f'{font_name}_regular.ttf'),
                'bold': join(font_dir, f'{font_name}_bold.ttf'),
                'italic': join(font_dir, f'{font_name}_italic.ttf'),
                'light': join(font_dir, f'{font_name}_light.ttf')}


class MainScreen(BoxLayout):
    connection_type_dropdown = ObjectProperty(None)

    def __init__(self, mock, **kwargs):
        super().__init__(**kwargs)
        self.connection_type_dropdown.items = ['TCP', 'Serial']
        self.connection_type_dropdown.bind(on_select=self.switch_column)
        self.mock = mock

    def switch_column(self, instance, value):
        self.ids.column_container.clear_widgets()
        if value == 'TCP':
            self.ids.column_container.add_widget(TCPColumn(self.mock))
            instance.text = value

        elif value == 'Serial':
            self.ids.column_container.add_widget(SerialColumn(self.mock))
            instance.text = value


class ConnectionIconLogHandler(logging.Handler):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback

    def emit(self, record):
        try:
            log_message = self.format(record)
            self.callback(log_message)
        except Exception:  # pylint: disable=broad-exception-caught
            self.handleError(record)


class TransportColumn(BoxLayout):
    content = ObjectProperty(None)
    hardware_dropdown = ObjectProperty(None)
    feed_interval = ObjectProperty(None)
    no_print = ObjectProperty(None)
    connect_button = ObjectProperty(None)
    connection_icon = ObjectProperty(None)
    icon_failure_color = ListProperty()
    icon_success_color = ListProperty()
    icon_default_color = ListProperty()

    def __init__(self, mock, content_class, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.connect_button.bind(on_release=self.connect_button_on_release)
        self.hardware_dropdown.bind(on_select=self.select_hardware)
        Window.bind(on_request_close=self.on_request_close)
        self.mock = mock
        self.mock_thread = None
        self.hardware_dropdown.items = HardwareConfig.get_all_config_names()
        if "agatka.yaml" in self.hardware_dropdown.items:
            self.hardware_dropdown.text = "agatka.yaml"
        else:
            self.hardware_dropdown.text = self.hardware_dropdown.items[-1]

        self.connection_icon.icon_color = self.icon_default_color
        self.custom_log_handler = ConnectionIconLogHandler(self.handle_log_message)
        logger = logging.getLogger("main")
        for h in logger.handlers:
            if isinstance(h, ConnectionIconLogHandler):
                logger.removeHandler(h)
        if not any(isinstance(h, ConnectionIconLogHandler) for h in logger.handlers):
            logger.addHandler(self.custom_log_handler)

        self.transport_content = content_class()
        self.content.add_widget(self.transport_content)

    def handle_log_message(self, log_message):
        if "connected" in log_message.lower():
            self.connection_icon.icon_color = self.icon_success_color
        elif "error" in log_message.lower():
            self.connection_icon.icon_color = self.icon_failure_color

    def select_hardware(self, instance, value):
        instance.text = value

    def connect_button_on_release(self, instance):
        if self.mock.should_run:
            self.stop_connection()
            self.connect_button.text = 'Connect'
        else:
            self.start_connection()
            self.connect_button.text = 'Disconnect'

    def start_connection(self):
        if self.mock.should_run is False:
            self._wait_for_mock_thread_to_stop()

            transport_settings = self.transport_content.pack_settings()
            mock_settings = MockSettings(transport_settings, self.hardware_dropdown.text,
                                         self.feed_interval.text,
                                         self.no_print.active)

            partial_mock_start = partial(self.mock.start, mock_settings)
            self.mock_thread = threading.Thread(target=partial_mock_start, daemon=True)
            self.mock_thread.start()
        else:
            self.mock.log_message(f"ALREADY RUNNING {datetime.now()}")
            self.connection_icon.icon_color = self.icon_success_color

    def stop_connection(self):
        self.mock.stop()
        self._wait_for_mock_thread_to_stop()
        self.mock.log_message(f"CONNECTION STOPPED {datetime.now()}")
        self.connection_icon.icon_color = self.icon_default_color

    def _wait_for_mock_thread_to_stop(self):
        if self.mock_thread is not None and self.mock_thread.is_alive():
            self.mock.log_message('Waiting for mock_thread to stop')
            self.mock_thread.join()

    def on_request_close(self, instance):
        self.mock.should_run = False
        self._wait_for_mock_thread_to_stop()


class TCPColumn(TransportColumn):

    def __init__(self, mock, **kwargs):
        super().__init__(mock, TcpColumnContent, **kwargs)


class SerialColumn(TransportColumn):

    def __init__(self, mock, **kwargs):
        super().__init__(mock, SerialColumnContent, **kwargs)


class StandaloneMock:
    def __init__(self):
        self.should_run = False
        self.manager = CommunicationManager()
        self.setup_loggers()
        self._logger = logging.getLogger("main")
        self._dynamixel_positions = {}
        self._lamp_pressure_ranges = {}

    def stop(self):
        self.should_run = False

    def start(self, connection_config: MockSettings):
        transport_settings = connection_config.transport_settings
        self.config = HardwareConfig(connection_config.hardware_config_name)

        if isinstance(transport_settings, TcpSettings):
            self.manager.change_transport_type(TransportType.TCP)
            transport_name = 'TCP'

        elif isinstance(transport_settings, SerialSettings):
            self.manager.change_transport_type(TransportType.SERIAL)
            transport_name = 'Serial'
        else:
            raise NotImplementedError('Unknown Transport Settings class passed')

        self.feed_send_delay = connection_config.feed_interval
        self.no_print = connection_config.no_print
        self.last_feed_update = time.perf_counter()

        self._dynamixel_positions.clear()
        self._lamp_pressure_ranges.clear()
        self._setup_heating_lamp_handling()
        self.manager.connect(transport_settings)

        self.log_message(f'Standalone mock is running, connection type : {transport_name}, '
                         f'with settings: {vars(transport_settings)}')

        self.log_message(f"CONNECTED {datetime.now()}")

        self.should_run = True
        self.receive_send_loop()

    def log_message(self, message):
        self._logger.info(message)

    def setup_loggers(self):
        self._logger = logging.getLogger("main")
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        fmt = '[%(asctime)s] [%(levelname)s] %(message)s'
        log_formatter = logging.Formatter(fmt=fmt)

        log_file_path = Path(sys.argv[0]).resolve().parent
        while log_file_path.name != 'rocket_ground_station':
            log_file_path = log_file_path.parent
        log_file_path = log_file_path.joinpath('logs')
        Path(log_file_path).mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            join(str(log_file_path),
                 f'Standalone_mock_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log'))

        console_handler = logging.StreamHandler(sys.stdout)

        file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)
        self._logger.addHandler(file_handler)
        self._logger.addHandler(console_handler)

    def get_response_id_for_action(self, frame_action, nack_weight=0, snack_weight=0):
        ack_weights = [1 - nack_weight, nack_weight]
        sack_weights = [1 - snack_weight, snack_weight]
        action = random.choices([ids.ActionID.ACK, ids.ActionID.NACK], ack_weights, k=1)[0]
        if frame_action == ids.ActionID.REQUEST:
            action = ids.ActionID.RESPONSE
        if frame_action == ids.ActionID.SCHEDULE:
            action = random.choices([ids.ActionID.SACK, ids.ActionID.SNACK], sack_weights, k=1)[0]
        return action

    def _setup_heating_lamp_handling(self):
        conf_dict = self.config.as_dict()
        heating_lamps: dict = conf_dict["devices"]["heatinglamp"]
        sensors: dict = conf_dict["devices"]["sensor"]
        pistons: dict = conf_dict["devices"].get("piston", {})
        sensors.update(pistons)

        for heating_lamp in heating_lamps.values():
            print(heating_lamp["dependencies"])
            sensor_name = heating_lamp["dependencies"]["pressure_sensor"]
            target_pressure = heating_lamp["target_pressure"]
            lower_range = target_pressure - target_pressure * 0.4
            upper_range = target_pressure + target_pressure * 0.4
            sensor_a = sensors[sensor_name]["a"]
            sensor_b = sensors[sensor_name]["b"]
            uncalibrated_lower_range = (lower_range - sensor_b) / sensor_a
            uncalibrated_upper_range = (upper_range - sensor_b) / sensor_a
            self._lamp_pressure_ranges[sensor_name] = (uncalibrated_lower_range, uncalibrated_upper_range)

    def handle_dynamixel_position(self, _frame: Frame):
        dynamixel_id = _frame.device_id
        self._dynamixel_positions[dynamixel_id] = _frame.payload[0]

    def handle_frame(self, _frame: Frame) -> list[Frame]:
        action = self.get_response_id_for_action(_frame.action)
        output_frames = []

        if (_frame.device_type == ids.DeviceID.DYNAMIXEL and
            _frame.action == ids.ActionID.SERVICE and
            _frame.operation ==  ids._DynamixelOperationID.POSITION): #pylint: disable=protected-access
            self.handle_dynamixel_position(_frame)

        if _frame.destination == ids.BoardID.BROADCAST:
            frame_params = _frame.as_dict()
            replacements = {'destination': _frame.source, 'source': _frame.destination, 'action': action}
            output_frames.append(Frame(**{**_frame.as_dict(), **replacements}))
            for board in [ids.BoardID.STASZEK, ids.BoardID.KROMEK]:
                frame_params['source'] = ids.BoardID.GRAZYNA
                frame_params['destination'] = board
                new_frame = self.handle_frame(Frame(**frame_params))[0]
                output_frames.append(new_frame)
            return output_frames

        replacements = {'destination': _frame.source, 'source': _frame.destination, 'action': action}
        output_frames.append(Frame(**{**_frame.as_dict(), **replacements}))
        return output_frames

    def _send_sensor_feed_frames(self, sensors: dict):
        for sensor_name, sensor_settings in sensors.items():
            source = ids.BoardID[sensor_settings["board"].upper()]
            device_id = sensor_settings["device_id"]
            data_type = ids.DataTypeID[sensor_settings["data_type"].upper()]
            if data_type == ids.DataTypeID.INT8:
                value = random.randint(-127, 127)
            elif data_type == ids.DataTypeID.UINT8:
                value = random.randint(0, 255)
            elif data_type == ids.DataTypeID.INT16:
                value = random.randint(-32767, 32767)
            else:
                value = random.randint(0, 65535)

            # Special handling for piston
            if device_id == 31:
                value = random.randint(0, 1000)

            if sensor_name in self._lamp_pressure_ranges:
                value_range = self._lamp_pressure_ranges[sensor_name]
                value = (value_range[1] - value_range[0]) * random.random() + value_range[0]


            frame = Frame(destination=ids.BoardID.GRAZYNA,
                          priority=ids.PriorityID.LOW,
                          action=ids.ActionID.FEED,
                          source=source,
                          device_type=ids.DeviceID.SENSOR,
                          device_id=device_id,
                          data_type=data_type,
                          operation=ids.OperationID.SENSOR.value.READ,
                          payload=(value,))
            self.manager.push(frame)
            try:
                self.manager.send()
            except TransportTimeoutError:
                break

            if not self.no_print:
                self.log_message(f"sent feed frame: {frame}")

    def _send_dynamixel_feed_frames(self, dynamixels: dict):
        for dynamixel_settings in dynamixels.values():
            source = ids.BoardID[dynamixel_settings["board"].upper()]
            device_id = dynamixel_settings["device_id"]
            data_type = ids.DataTypeID.INT16
            if device_id in self._dynamixel_positions:
                value = self._dynamixel_positions[device_id]
            else:
                value = random.randint(-2000, 4000)

            frame = Frame(destination=ids.BoardID.GRAZYNA,
                          priority=ids.PriorityID.LOW,
                          action=ids.ActionID.FEED,
                          source=source,
                          device_type=ids.DeviceID.DYNAMIXEL,
                          device_id=device_id,
                          data_type=data_type,
                          operation=ids.OperationID.DYNAMIXEL.value.POSITION,
                          payload=(value,))
            self.manager.push(frame)
            try:
                self.manager.send()
            except TransportTimeoutError:
                break

            if not self.no_print:
                self.log_message(f"sent feed frame: {frame}")

    def send_feed_frame(self):
        conf_dict = self.config.as_dict()
        dynamixels: dict = conf_dict["devices"]["dynamixel"]
        sensors: dict = conf_dict["devices"]["sensor"]
        pistons: dict = conf_dict["devices"].get("piston", {})
        sensors.update(pistons)
        self._send_sensor_feed_frames(sensors)
        self._send_dynamixel_feed_frames(dynamixels)

    def receive_send_loop(self):
        while self.should_run:
            try:
                frame = self.manager.receive()
            except TransportTimeoutError:
                continue
            except UnregisteredCallbackError as e:
                frame = e.frame
            except (KeyboardInterrupt, SystemExit):
                break
            finally:
                if time.perf_counter() > self.last_feed_update + float(self.feed_send_delay):
                    self.send_feed_frame()
                    self.last_feed_update = time.perf_counter()

            for frame in self.handle_frame(frame):
                self.manager.push(frame)
                if not self.no_print:
                    self.log_message(f"pushed frame: {frame}")
                try:
                    self.manager.send()
                except TransportTimeoutError:
                    continue


if __name__ == '__main__':
    StandaloneMockUI().run()
