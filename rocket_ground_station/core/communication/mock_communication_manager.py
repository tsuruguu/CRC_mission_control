import random
import time
from unittest.mock import Mock
import os

from rocket_ground_station.core.communication import CommunicationManager, Frame, ids
from rocket_ground_station.core.communication.exceptions import UnregisteredCallbackError
from rocket_ground_station.core.configs import AppConfig

#  TransportTimeoutError)

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.exceptions import TransportTimeoutError # pylint: disable=import-error
else:
    from rocket_ground_station.core.communication.exceptions import TransportTimeoutError # pylint: disable=ungrouped-imports

from collections import deque
from rocket_ground_station.core.communication.serial_transport import (SerialTransport,
                                                                       SerialOptions,
                                                                       SerialInfo)
from rocket_ground_station.core.communication.transport import TransportInfo


class FeedOrigin:
    def __init__(self, device, interval=2, interval_random_margin=0,
                 default_min_value=-100, default_max_value=100):
        self.timestamp = time.time()
        self.device = device
        self._interval = interval
        self._interval_random_margin = interval_random_margin
        self._default_min_value = default_min_value
        self._default_max_value = default_max_value

    def get_feed(self) -> Frame:
        if time.time() > self.timestamp + self._interval:
            frame = self._create_feed_frame(self.device)
            self.timestamp = time.time() + self._interval
            self.timestamp += random.uniform(0, self._interval_random_margin)
            return frame
        return None

    def _create_feed_frame(self, device) -> Frame:
        min_value = getattr(device, 'open_pos', self._default_min_value)
        max_value = getattr(device, 'closed_pos', self._default_max_value)
        min_value = min_value if min_value else self._default_min_value
        max_value = max_value if max_value else self._default_max_value
        data_type = ids.DataTypeID[str.upper(getattr(device, 'data_type', 'float'))]
        device_type = ids.DeviceID[str.upper(device.device_type)]

        if data_type == ids.DataTypeID.INT8:
            payload = random.randint(-127, 127)
        elif data_type == ids.DataTypeID.UINT8:
            payload = random.randint(0, 255)
        elif data_type == ids.DataTypeID.INT16:
            payload = random.randint(-32767, 32767)
        else:
            payload = random.uniform(min_value, max_value)

        # Special handling for piston
        if device.id == 31:
            payload = random.randint(0, 1000)

        # Special handling for dynamixels
        if device_type == ids.DeviceID.DYNAMIXEL:
            payload = random.randint(-2000, 4000)

        replacements = {'destination': ids.BoardID.GRAZYNA, 'priority': ids.PriorityID.LOW,
                        'action': ids.ActionID.FEED, 'source': device.board,
                        'device_type': device_type, 'device_id': device.id,
                        'data_type': data_type, 'operation': device.feed_ids[0], 'payload': (payload,)}
        return Frame(**replacements)


class MockCommunicationManager(CommunicationManager):
    def __init__(self):
        super().__init__()
        self._queue = deque()
        self._port_name = 'MOCK'
        self._baudrate = 115200
        self._is_connected = False
        self._read_timeout = 0
        self._write_timeout = 0
        self._feed_origins = []
        self._initialize_transport()

    def change_transport_type(self, transport_type: str):
        self._initialize_transport()

    @property
    def transport_info(self) -> TransportInfo:
        return SerialInfo(active=self._transport.is_open,
                          transport_type='SerialTransport',
                          port=self._port_name,
                          baudrate=self._baudrate)

    def _initialize_transport(self):
        self._transport = Mock(SerialTransport, name='serial transport mock')
        self._transport.port = self._port_name
        self._transport.baudrate = self._baudrate
        options = SerialOptions()
        options.port = (self._port_name,)
        options.baudrate = (self._baudrate,)
        self._transport.options = lambda: options
        self._transport.read_timeout = self._read_timeout
        self._transport.write_timeout = self._write_timeout
        self._transport.is_open = False
        self._transport.write = lambda frame_bytes: self._queue.append(self._protocol.decode(frame_bytes))
        self._transport.close = lambda: (self._queue.clear(), setattr(self._transport, 'is_open', False))
        self._transport.open = lambda *args: setattr(self._transport, 'is_open', True)

    def _get_response_id_for_action(self, frame_action, nack_weight=0, snack_weight=0):
        ack_weights = [1 - nack_weight, nack_weight]
        sack_weights = [1 - snack_weight, snack_weight]
        action = random.choices([ids.ActionID.ACK, ids.ActionID.NACK], ack_weights, k=1)[0]
        if frame_action == ids.ActionID.REQUEST:
            action = ids.ActionID.RESPONSE
        if frame_action == ids.ActionID.SCHEDULE:
            action = random.choices([ids.ActionID.SACK, ids.ActionID.SNACK], sack_weights, k=1)[0]
        return action

    def _handle_frame(self, frame) -> Frame:
        action = self._get_response_id_for_action(frame.action)
        if frame.destination == ids.BoardID.BROADCAST:
            frame_params = frame.as_dict()
            for board in [ids.BoardID.STASZEK, ids.BoardID.KROMEK]:
                frame_params['source'] = ids.BoardID.GRAZYNA
                frame_params['destination'] = board
                new_frame = Frame(**frame_params)
                self._queue.append(new_frame)

        replacements = {'destination': frame.source, 'source': frame.destination, 'action': action}
        return Frame(**{**frame.as_dict(), **replacements})

    def receive(self) -> Frame:
        frame = None
        if self._queue:
            frame = self._queue.popleft()
            frame = self._handle_frame(frame)
        else:
            if any(self._feed_origins):
                for origin in sorted(self._feed_origins, key=lambda x: x.timestamp):
                    frame = origin.get_feed()
                    if frame is not None:
                        break
            if frame is None:
                # No frame received, raise the same exception as SerialTransport would in such case
                raise TransportTimeoutError('Timeout while reading from a serial port')

        try:
            self._callbacks[frame](frame)
        except KeyError:
            raise UnregisteredCallbackError(frame)
        return frame

    def set_devices(self, devices):
        self._queue.clear()
        self._feed_origins = []
        for device in devices.values():
            if len(device.feed_ids) > 0:
                origin = FeedOrigin(device, interval=AppConfig().integrated_mock_feed_send_rate)
                self._feed_origins.append(origin)
