from typing import Union
import os
import socket
import threading
import struct
import time
from ipaddress import IPv4Address
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivymd.uix.boxlayout import MDBoxLayout
from logging import getLogger

from rocket_ground_station.core.communication import CommunicationManager, TransportType
from rocket_ground_station.core.communication.mock_communication_manager import MockCommunicationManager
from rocket_ground_station.components.buttons import SpaceFlatButton
from rocket_ground_station.components.buttons import SpacePrimaryButton
from rocket_ground_station.components.popups.space_popup import SpacePopup
from rocket_ground_station.components.popups.message import Message
from rocket_ground_station.core.communication.protocol import GroundStationProtocol

from rocket_ground_station.core.communication.transport import TransportSettings

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.tcp_transport import TcpSettings # pylint: disable=import-error
    from python_sw_core.communication.serial_transport import SerialSettings, SerialOptions # pylint: disable=import-error
    from python_sw_core.communication.exceptions import TransportTimeoutError # pylint: disable=import-error
else:
    from rocket_ground_station.core.communication.tcp_transport import TcpSettings # pylint: disable=ungrouped-imports
    from rocket_ground_station.core.communication.serial_transport import SerialOptions, SerialSettings # pylint: disable=ungrouped-imports
    from rocket_ground_station.core.communication.exceptions import TransportTimeoutError

class Connect(SpacePopup):

    def __init__(self, cm: CommunicationManager, halt_popup: bool = False, **kwargs) -> None:
        self.communication = cm
        cancel = SpaceFlatButton(text='CANCEL')
        cancel.bind(on_release=self.dismiss)
        connect = SpacePrimaryButton(text='CONNECT')
        connect.bind(on_release=self.connect)
        super().__init__(title='Connect to the rocket',
                         content=ConnectContent(cm),
                         buttons=[cancel, connect],
                         size_hint=(0.5, 0.5), **kwargs)
        if not halt_popup:
            self.open()

    def connect(self, _caller) -> None:
        """
        Connects ground station to the rocket and closes the popup.
        """
        try:
            transport_parameters: TransportSettings = self.content_cls.pack_transport_parameters()
            if not isinstance(self.communication, MockCommunicationManager):
                transport_parameters.validate()
        except ValueError as err:
            Message(title='Error: transport parameters invalid', message=str(err))
            return

        try:
            self.communication.connect(transport_parameters)
        # This handling of transporttimeouterror is a hack, but will do for now for rust implementation's sake
        # Since there is a problem with discerning rust io:error type for connection open and access timeout
        # we will just detect connection being unable to open like this
        # Ideally we should do it on rust side and return appropriate error but that's a task for another day
        except (IOError, TransportTimeoutError) as err:
            Message(title='Error: could not open the transport connection', message=str(err))
        self.dismiss()


class ConnectContent(MDBoxLayout):
    """
    Implements a content of a popup window for communication parameters specification.
    """
    transport_spinner = ObjectProperty()

    def __init__(self, communication: CommunicationManager, **kwargs) -> None:
        super().__init__(**kwargs)
        self.transport_spinner.items = [e.name for e in TransportType]
        self.transport_spinner.text = self.transport_spinner.items[0]
        self.communication = communication
        self.content_widget = None
        self.change_transport_content(self.transport_spinner.items[0])

    def pack_transport_parameters(self) -> TransportSettings:
        return self.content_widget.pack_transport_parameters()

    def change_transport_content(self, transport_type: Union[TransportType, str]):
        transport_type = TransportType[transport_type]

        if self.content_widget is not None:
            self.remove_widget(self.content_widget)

        if transport_type == TransportType.SERIAL:
            self.content_widget = SerialTransportContent(self.communication)

        elif transport_type == TransportType.TCP:
            self.content_widget = TcpTransportContent(self.communication)

        self.add_widget(self.content_widget)
        self.transport_spinner.text = transport_type.name


class SerialTransportContent(MDBoxLayout):
    """
    Implements a content of a popup window for communication parameters specification.
    """
    port_spinner = ObjectProperty()
    baud_spinner = ObjectProperty()

    def __init__(self, communication: CommunicationManager, **kwargs) -> None:
        super().__init__(**kwargs)
        communication.change_transport_type(TransportType.SERIAL)
        transport_options: SerialOptions = communication.transport_options
        default_port = transport_options.get_default_port()
        self.port_spinner.items = sorted(transport_options.port, reverse=True) or ['No serial ports found']
        self.baud_spinner.items = [str(baud) for baud in sorted(transport_options.baudrate, reverse=True)]
        #Set the default port if found, otherwise fall back to the last port
        self.port_spinner.text = default_port if default_port is not None else self.port_spinner.items[0]
        self.baud_spinner.text = self.baud_spinner.items[0]

    def pack_transport_parameters(self) -> SerialSettings:
        return SerialSettings(port=self.port_spinner.text, baudrate=int(self.baud_spinner.text))


class TcpTransportContent(MDBoxLayout):
    """
    Implements a content of a popup window for communication parameters specification.
    """
    address_input = ObjectProperty()
    port_input = ObjectProperty()

    def __init__(self, communication: CommunicationManager, **kwargs) -> None:
        super().__init__(**kwargs)
        communication.change_transport_type(TransportType.TCP)

        # Add autodiscovery button
        self.discover_button = SpaceFlatButton(
            text="Autodiscover",
            pos_hint={"center_x": 0.5},
            on_release=self.start_autodiscovery
        )
        self.add_widget(self.discover_button)
        self._discovery_thread = None
        self._discovery_running = False
        self.logger = getLogger("main")

    def pack_transport_parameters(self) -> TcpSettings:
        return TcpSettings(address=self.address_input.text, port=int(self.port_input.text))

    def start_autodiscovery(self, *args):
        """Start the autodiscovery process in a separate thread"""
        if self._discovery_running:
            return

        self.discover_button.text = "Discovering..."
        self.discover_button.disabled = True
        self._discovery_running = True

        self._discovery_thread = threading.Thread(
            target=self._run_autodiscovery,
            daemon=True
        )
        self._discovery_thread.start()

    def _run_autodiscovery(self):
        """Run the autodiscovery process and update UI with results"""
        try:
            result = self.discover_proxy()
            if result:
                ip, port = result
                Clock.schedule_once(lambda _: self._update_discovery_result(ip, port), 0)
            else:
                Clock.schedule_once(lambda _: self._discovery_finished(False), 0)
        except Exception as e: # pylint: disable=broad-except
            self.logger.info(f"Autodiscovery error: {e}")
            Clock.schedule_once(lambda dt: self._discovery_finished(False), 0)

    def _update_discovery_result(self, ip, port):
        """Update UI with discovered values"""
        self.address_input.text = ip
        self.port_input.text = str(port)
        self._discovery_finished(True)

    def _discovery_finished(self, success):
        """Reset discovery button state"""
        self.discover_button.disabled = False
        self.discover_button.text = "Autodiscover"
        if not success:
            Message(title='Autodiscovery', message='No proxy discovered on the network')
            self.logger.info("No proxy discovered on the network")
        self._discovery_running = False

    def discover_proxy(self, timeout=5.0, magic=0x06):
        """
        Listen for proxy autodiscovery broadcasts.

        The broadcast format is:
        - 1 byte magic number
        - 1 byte service type
        - 4 bytes IP address
        - 2 bytes port number
        - 4 bytes CRC32 MPEG2 checksum

        Returns:
            tuple: (ip_address, port) if discovery successful, None otherwise
        """
        # Create UDP socket for listening
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(timeout)
        sock.bind(('0.0.0.0', 41234))  # Bind to any port
        bound_port = sock.getsockname()[1]

        self.logger.info(f"Autodiscovery listening on port {bound_port}")

        try:
            end_time = time.time() + timeout
            while time.time() < end_time and self._discovery_running:
                try:
                    data, _ = sock.recvfrom(12)  # Expected packet size is 12 bytes

                    if len(data) != 12:
                        continue

                    # Check magic number
                    if data[0] != magic:
                        continue

                    # Extract data
                    service_type = data[1]
                    payload = data[:8]  # All but CRC
                    received_crc = data[-4:]  # Last 4 bytes

                    # self.logger.info data
                    self.logger.info(f"Received data: {data.hex()}")
                    self.logger.info(f"Service type: {service_type}")
                    self.logger.info(f"Payload: {payload.hex()}")
                    self.logger.info(f"Payload length: {len(payload)}")

                    if service_type != 0x01:
                        self.logger.info(f"Invalid service type: {service_type}")
                        continue

                    # Parse IP and port
                    ip_bytes = data[2:6]
                    port_bytes = data[6:8]

                    self.logger.info(f"IP bytes: {ip_bytes.hex()}")
                    self.logger.info(f"Port bytes: {port_bytes.hex()}")

                    ip = str(IPv4Address(ip_bytes))
                    port = struct.unpack(">H", port_bytes)[0]  # Big endian unsigned short

                    self.logger.info(f"IP: {ip}")
                    self.logger.info(f"Port: {port}")

                    # So it turns out that our crc pre processing is a lil bit flawed,
                    # we are padding even 4 divisible byte arrays
                    # (If you are curious I encourage you to go and walk over the padding line
                    # in the function itself, for example for 8 byte long data)
                    # Ending with a situation where we pad 8 byte long payload
                    # of a discovery frame with 4 bytes of zeros
                    # This results in a CRC mismatch even though data is correct
                    # In order to circumvent the issue
                    # I have added some new optional arguments to the calculate_crc function
                    # The current behavior might be some leftover code
                    # due to past compatiblity requirement with electronics
                    calculated_crc = GroundStationProtocol.calculate_crc(payload,
                                                                         skip_padding=True,
                                                                         return_endianess='big')

                    self.logger.info(f"Calculated CRC: {calculated_crc.hex()}")
                    self.logger.info(f"Received CRC: {received_crc.hex()}")

                    if calculated_crc != received_crc:
                        self.logger.info("CRC mismatch in discovery packet")
                        continue

                    self.logger.info(f"Discovered proxy at {ip}:{port}")
                    return (ip, port)

                except socket.timeout:
                    continue

            return None
        finally:
            sock.close()
