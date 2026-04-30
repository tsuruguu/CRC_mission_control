from typing import Optional
from collections import deque

import serial
import serial.tools.list_ports
import logging
import os

from rocket_ground_station.core.communication.exceptions import TransportNotFoundError

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.exceptions import (ClosedTransportError,  # pylint: disable=import-error
                                                         TransportError,
                                                         TransportTimeoutError)
else:
    from rocket_ground_station.core.communication.exceptions import (ClosedTransportError, # pylint: disable=ungrouped-imports
                                                                    TransportError,
                                                                    TransportTimeoutError)

from rocket_ground_station.core.communication.transport import (TransportOptions,
                                                                TransportInfo,
                                                                TransportSettings,
                                                                Transport)


class SerialOptions(TransportOptions):
    def __init__(self):
        self.port: tuple[str, ...] = tuple(comport.device for comport in serial.tools.list_ports.comports())
        self.baudrate: tuple[int, ...] = 9600, 19200, 38400, 57600, 115200

    def get_default_port(self):
        logger = logging.getLogger('main')
        default_port_name = 'USB Serial Port'
        for port in serial.tools.list_ports.comports():
            if default_port_name in port.description:
                logger.info(f'Found default serial port: {port.device}')
                return port.device
        logger.info(f'Default serial port with device name: {default_port_name}, not found')
        return None


class SerialInfo(TransportInfo):
    def __init__(self, active: bool, transport_type: str, port: str, baudrate: int):
        self.status = 'Active' if active else 'Inactive'
        self.transport_type = transport_type
        self.port = port
        self.baudrate = baudrate

    def __dict__(self) -> dict:
        return {
            'Status': self.status,
            'Type': self.transport_type,
            'Port': self.port,
            'Baudrate': self.baudrate
        }


class SerialSettings(TransportSettings):
    def __init__(self, port: str, baudrate: int):
        self.port = port
        self.baudrate = baudrate

    @classmethod
    def options(cls) -> SerialOptions:
        return SerialOptions()

    def validate(self):
        opts = self.options()

        if self.port not in opts.port:
            raise ValueError(f'Port: "{self.port}" does not exist')

        if self.baudrate not in opts.baudrate:
            raise ValueError(f'Baudrate: "{self.baudrate}" is not available')


class SerialTransport(Transport):
    """
    Serial port bidirectional transport interface.
    """

    def __init__(self) -> None:
        self._serial = serial.Serial()
        self._cache = deque()
        self._cache_size = 8192

    @property
    def port(self) -> str:
        """
        Property for currently used serial port name. Returns None if not opened.
        """
        return self._serial.port if self.is_open else None

    @property
    def baudrate(self) -> int:
        """
        Property for currently used baudrate. Returns None if not opened.
        """
        return self._serial.baudrate if self.is_open else None

    @property
    def read_timeout(self) -> int:
        """
        Property for timeout of the serial port read action in seconds.
        """
        return self._serial.timeout

    @property
    def write_timeout(self) -> int:
        """
        Property for timeout of the serial port write action in seconds.
        """
        return self._serial.write_timeout

    @classmethod
    def options(cls) -> SerialOptions:

        """
        Options available to supply while establishing a transport connection.
        """

        return SerialSettings.options()

    @property
    def info(self) -> SerialInfo:

        """
        Information regarding current transport state.
        """
        return SerialInfo(active=self.is_open,
                          transport_type=type(self).__name__,
                          port=self.port,
                          baudrate=self.baudrate)

    @property
    def is_open(self) -> bool:
        """
        Property checking if the transport is open.
        :return: True if the transport is open, False otherwise
        """
        return self._serial.is_open

    def open(self, settings: SerialSettings, read_timeout: float = 0,
             write_timeout: Optional[float] = 1) -> None:
        """
        Opens serial port with the given arguments.
        :param settings: used to set up connection
        :param read_timeout: read timeout in seconds, None for forever, 0 for non-blocking
        :param write_timeout: write timeout in seconds, same as read timeout
        """
        try:
            port = settings.port
            baudrate = settings.baudrate
            self._serial = serial.Serial(port, baudrate, timeout=read_timeout,
                                         write_timeout=write_timeout)
        except ValueError:
            raise TransportError('Serial port parameters are out of range')
        except serial.SerialException:
            raise TransportNotFoundError('Serial port cannot be found or configured')

    def close(self) -> None:
        """
        Closes the transport.
        """
        self._serial.close()

    def write(self, data: bytes) -> None:
        """
        Writes bytes of data to the port.
        :param data: data bytes to send
        """
        try:
            self._serial.write(data)
        except serial.SerialTimeoutException:
            raise TransportTimeoutError('Timeout while writing to a serial port')
        except serial.SerialException:
            raise ClosedTransportError('Writing to a closed serial port')

    def read(self, number_of_bytes: int = 1) -> bytes:
        """
        Reads bytes of data from the port. Buffer additional data.
        :param number_of_bytes: number of bytes to be read
        :return: requested number of bytes.
        """

        # If requested amount of bytes is bigger than max cache size, raise an exception
        if number_of_bytes > self._cache_size:
            raise ValueError(
                f'Requested amount of bytes: {number_of_bytes}, '
                f'exceeds max cache size of: {self._cache_size}. '
                f'This read will never succeed. Please perform a smaller read.')

        # If buffer has exact amount of bytes requested or bigger, return immediately skipping transport read
        if number_of_bytes <= len(self._cache):
            return bytes(self._cache.popleft() for _ in range(number_of_bytes))

        # Read as many bytes as possible from transport and return requested amount
        try:
            available_bytes = self._serial.in_waiting
            available_space = self._cache_size - len(self._cache)
            bytes_to_read = available_bytes if available_bytes < available_space else available_space
            self._cache.extend(self._serial.read(bytes_to_read))
        except serial.SerialException:
            raise ClosedTransportError('Reading from a closed serial port')

        # Timeout if the amount read was still smaller than amount of bytes requested
        if len(self._cache) < number_of_bytes:
            raise TransportTimeoutError('Timeout while reading from a serial port')

        # Return requested amount of bytes
        return bytes(self._cache.popleft() for _ in range(number_of_bytes))

    @property
    def read_buffer_size(self) -> int:
        """
        Returns the number of bytes in the read buffer.
        """
        return len(self._cache)
