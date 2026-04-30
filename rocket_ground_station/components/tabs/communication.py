from typing import Dict
from kivy.clock import Clock
from kivy.properties import BooleanProperty, NumericProperty, ObjectProperty, StringProperty
import os
from rocket_ground_station.components.frame_logger import FrameLogger
from rocket_ground_station.components.label import SpaceLabel
from rocket_ground_station.core.communication import CommunicationManager, ids, Frame
from rocket_ground_station.core.communication.exceptions import (ChecksumMismatchError,
                                                                 MissingHeaderError,
                                                                 UnregisteredCallbackError)
from rocket_ground_station.core.configs import AppConfig

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.exceptions import (TransportError,        # pylint: disable=import-error
                                                         TransportTimeoutError) # pylint: disable=import-error
else:
    from rocket_ground_station.core.communication.exceptions import (TransportError,        # pylint: disable=ungrouped-imports
                                                                     TransportTimeoutError)

from rocket_ground_station.components.popups import Connect, Message, BinaryQuestion
from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.components.device_widgets import DeviceWidget
from rocket_ground_station.components.tabs.tab import Tab

class Communication(Tab):
    """
    Implements a tab that allows user to monitor the connection with the rocket.
    """
    status_layout = ObjectProperty()
    frame_logger: FrameLogger = ObjectProperty()
    _port, _baudrate = StringProperty('--'), StringProperty('--')
    _write_timeout, _read_timeout = StringProperty('--'), StringProperty('--')
    sent, received = NumericProperty(), NumericProperty()
    _is_connected = BooleanProperty(False)
    mismatched_crc_count = NumericProperty(0)
    missing_header_count = NumericProperty(0)
    unregistered_frames_count = NumericProperty(0)

    def __init__(self, cm: CommunicationManager, **tab_kwargs) -> None:
        """
        :param cm: instance of application's communication interface
        """
        super().__init__(**tab_kwargs)
        self._communication = cm
        self._was_connected = False
        Clock.schedule_interval(self._receive, AppConfig().receive_dt)
        Clock.schedule_interval(self._send, AppConfig().send_dt)
        Clock.schedule_interval(self._send_keep_alive, AppConfig().keepalive_interval)
        self.save_to_file = AppConfig().save_frames_to_file
        self.max_receive_batch_size = AppConfig().max_receive_batch_size
        self.max_send_batch_size = AppConfig().max_send_batch_size
        if self.save_to_file:
            self.frame_logger.init_file(AppConfig().log_to_frame_file_dt)
        self.register_event_type('on_connection_start')
        self.register_event_type('on_connection_lost')
        self.register_event_type('on_connection_stop')
        self._labels_dict = {}
        self.update_status({'Status': 'Inactive', 'Type': 'None'})
        self._logger.info('Communication tab initialized')
        self._read_buffer_interval = None

    @property
    def is_connected(self) -> bool:
        """
        Returns True if the app is connected to the rocket, False otherwise.
        """
        return self._is_connected

    def connect(self) -> None:
        """
        Opens popup to configure connection with hardware
        """
        Connect(self._communication)

    def disconnect(self) -> None:
        """
        Closes connection with hardware
        """

        def on_answer(disconnect: bool) -> None:
            if not disconnect:
                return
            self._communication.disconnect()

        BinaryQuestion(question='Are you sure you want to disconnect?',
                       on_answer=on_answer)

    def _receive(self, duration: float) -> None:
        """
        Called every interval to receive frames through communication manager.
        :param duration: seconds passed from the last scheduled call
        """
        self._is_connected = self._communication.is_connected
        if not self._was_connected and self.is_connected:
            self.dispatch('on_connection_start')
        if not self.is_connected and self._was_connected:
            self.dispatch('on_connection_stop')
        if self.is_connected:
            for _ in range(self.max_receive_batch_size):
                try:
                    frame = self._communication.receive()
                except TransportTimeoutError:
                    break
                except ChecksumMismatchError:
                    self.mismatched_crc_count += 1
                except MissingHeaderError:
                    self.missing_header_count += 1
                except UnregisteredCallbackError as error:
                    self.unregistered_frames_count += 1
                    self.frame_logger.log_frame(error.frame, received=True, error=True)
                except TransportError as error:
                    self._logger.error('Transport Error: ' + str(error))
                    Message.create(LogLevel.ERROR, 'Transport Error: ' + str(error))
                    self.dispatch('on_connection_lost')
                    break
                else:
                    self.received += 1
                    is_error = frame.action in (ids.ActionID.NACK.value, ids.ActionID.SNACK.value)
                    self.frame_logger.log_frame(frame, received=True, error=is_error)

    def _send(self, duration: float) -> None:
        """
        Called every interval to send frames through communication manager.
        :param duration: seconds passed from the last scheduled call
        """
        if self.is_connected:
            for _ in range(self.max_send_batch_size):
                try:
                    frame = self._communication.send()
                # This handling of transporttimeouterror is a hack,
                # but will do for now for rust implementation's sake
                # Since there is a problem with discerning rust
                # io:error type for connection close and timeout
                # we will just detect connection breaking like this
                # Ideally we should do it on rust side and return appropriate error
                # but that's a task for another day
                except (TransportError, TransportTimeoutError) as error:
                    self._logger.error('Transport Error: ' + str(error))
                    Message.create(LogLevel.ERROR, 'Transport Error: ' + str(error))
                    self.dispatch('on_connection_lost')
                    break
                else:
                    if frame is not None:
                        self.sent += 1
                        self.frame_logger.log_frame(frame, received=False)
                    else:
                        break

    def _send_keep_alive(self, duration: float):
        """
        Called every interval to send a keepalive frame through communication manager.
        :param duration: seconds passed from the last scheduled call
        """
        if not self.is_connected:
            return

        keepalive_frame = Frame(destination=ids.BoardID.KROMEK,
                                priority=ids.PriorityID.LOW,
                                action=ids.ActionID.HEARTBEAT,
                                source=ids.BoardID.GRAZYNA,
                                device_type=ids.DeviceID.KEEPALIVE,
                                device_id=0x01,
                                data_type=ids.DataTypeID.NO_DATA,
                                operation=ids.OperationID.KEEPALIVE.value.KEEPALIVE,
                                payload=tuple())

        self._communication.push(keepalive_frame)

    def on_close(self):
        self.frame_logger.close_file()
        self.disconnect()

    def update_status(self, status_information: dict):
        for key, value in status_information.items():
            if key in self._labels_dict:
                self._labels_dict[key].text = str(value)
            else:
                key_label = SpaceLabel(text=str(key).capitalize())
                value_label = SpaceLabel(text=str(value))
                self.status_layout.add_widget(key_label)
                self.status_layout.add_widget(value_label)
                self._labels_dict[key] = value_label

    def clear_status(self):
        self.status_layout.clear_widgets()
        self._labels_dict.clear()

    def _update_read_buffer_size(self, dt):
        read_buffer_size = self._communication.read_buffer_size
        self.update_status({'Read Buffer in waiting': read_buffer_size})

    def on_connection_start(self) -> None:
        """
        Called when connection is established
        """
        self._was_connected = True
        status_information = self._communication.transport_info
        self._read_buffer_interval = Clock.schedule_interval(self._update_read_buffer_size, 0.25)
        self.clear_status()
        self.update_status(status_information.__dict__())
        self._logger.info('Connection established')

    def on_connection_stop(self) -> None:
        """
        Called when connection is stopped by user
        """
        self._was_connected = False
        status_information = self._communication.transport_info
        if self._read_buffer_interval is not None:
            self._read_buffer_interval.cancel()
        self.clear_status()
        self.update_status(status_information.__dict__())
        self._logger.info('Connection stopped')

    def on_connection_lost(self) -> None:
        """
        Called when connection is lost
        """
        self._logger.error('Connection lost!')
        self._communication.disconnect()
        self._was_connected = False
        status_information = self._communication.transport_info
        if self._read_buffer_interval is not None:
            self._read_buffer_interval.cancel()
        self.clear_status()
        self.update_status(status_information.__dict__())

    def on_hardware_load(self, device_widgets: Dict[str, DeviceWidget]) -> None:
        if device_widgets:
            self.frame_logger.current_devices = {key: (val.device_type.lower(), val.id)
                                                 for key, val in
                                                 device_widgets.items()}
