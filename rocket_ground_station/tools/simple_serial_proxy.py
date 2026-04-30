import asyncio
import logging
import os
from rocket_ground_station.core.communication.protocol import GroundStationProtocol
from rocket_ground_station.core.communication.exceptions import TransportError

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.exceptions import TransportTimeoutError # pylint: disable=import-error
else:
    from rocket_ground_station.core.communication.exceptions import TransportTimeoutError # pylint: disable=ungrouped-imports

from rocket_ground_station.core.communication.ids import HEADER_ID
from rocket_ground_station.core.communication.serial_transport import SerialTransport, SerialSettings
from collections import deque
from pathlib import Path
from os.path import join
import sys
from datetime import datetime
from argparse import ArgumentParser


class ProxyClient:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.send_queue = deque()
        self._should_stop = False

    @property
    def should_stop(self):
        return self._should_stop

    def get_key(self):
        return self.reader

    def stop(self):
        self._should_stop = True

    def push_data_to_send(self, data):
        self.send_queue.append(data)

    def get_data_to_send(self):
        return self.send_queue.popleft()

    async def write(self, data):
        self.writer.write(data)
        await self.writer.drain()

    async def readexactly(self, amount):
        return await self.reader.readexactly(amount)


class Proxy:

    def __init__(self):
        self.protocol = GroundStationProtocol()
        self.serial_transport = SerialTransport()
        self.transport_settings = None
        self.tcp_address = None
        self.tcp_port = None
        self.mirror_frames = False
        self.clients = {}
        self.setup_loggers()
        self._logger = logging.getLogger("main")
        self._send_queue = deque()

    def push_data_to_send(self, data):
        self._send_queue.append(data)

    def get_data_to_send(self):
        return self._send_queue.popleft()

    def setup_loggers(self):
        logger_main = logging.getLogger("main")
        logger_main.setLevel(logging.DEBUG)

        fmt = '[%(asctime)s] [%(levelname)s] %(message)s'
        log_formatter = logging.Formatter(fmt=fmt)

        log_file_path = Path(sys.argv[0]).resolve().parent
        while log_file_path.name != 'rocket_ground_station':
            log_file_path = log_file_path.parent
        log_file_path = log_file_path.joinpath('logs')
        Path(log_file_path).mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(
            join(str(log_file_path),
                 f'Proxy_{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log'))

        console_handler = logging.StreamHandler(sys.stdout)

        file_handler.setFormatter(log_formatter)
        console_handler.setFormatter(log_formatter)
        logger_main.addHandler(file_handler)
        logger_main.addHandler(console_handler)

    def add_client(self, reader, writer: asyncio.StreamWriter):
        client = ProxyClient(reader, writer)
        self.clients.update({client.get_key(): client})
        self._logger.info('Added new client')
        return client

    def remove_client(self, client):
        key = client.get_key()
        if key in self.clients:
            client.stop()
            self.clients.pop(key)
            self._logger.info('Removed client')

    def set_transport_options(self, options):
        if self.serial_transport.is_open:
            self._logger.error('Attempted changing options while transport is open')
            return

        self.transport_settings = options

    def set_tcp_server_options(self, address, port):
        self.tcp_address = address
        self.tcp_port = port
        self._logger.info(f'Server listen tcp socket set to {self.tcp_address}:{self.tcp_port}')

    def set_frame_mirroring(self, state):
        self.mirror_frames = state
        self._logger.info(f'Frame mirroring set to: {self.mirror_frames}')

    def close_transport(self):
        self.serial_transport.close()
        self._logger.info('Closed transport')

    def open_transport(self):
        self.serial_transport.open(self.transport_settings)
        self._logger.info('Opened transport')

    def reconnect_transport(self):
        self._logger.info('Attempting transport reconnect')
        self.close_transport()
        self.open_transport()
        self._logger.info('Transport reconnected')

    # Handle receiving data from ground station and forwarding it to clients
    async def handle_station_receive(self):
        while True:
            if self.serial_transport.is_open:
                try:
                    header = self.serial_transport.read(1)
                    if header != bytes([HEADER_ID]):
                        await asyncio.sleep(0)
                        continue
                    raw_frame = self.serial_transport.read(13)
                except TransportTimeoutError:
                    await asyncio.sleep(0)
                    continue

                clients_to_drop = []
                for client in self.clients.values():
                    try:
                        client.push_data_to_send(header + raw_frame)
                    except ConnectionResetError:
                        clients_to_drop.append(client)
                        continue
                for client in clients_to_drop:
                    self.remove_client(client)
                await asyncio.sleep(0)
            else:
                await asyncio.sleep(0.1)

    async def handle_station_send(self):
        while True:
            if not self._send_queue:
                await asyncio.sleep(0)
                continue

            data = self.get_data_to_send()

            try:
                self.serial_transport.write(data)
            except TransportError as error:
                self._logger.error(f'Serial Error: {error}')

    # Handle receiving data from client and send it to ground station
    async def handle_client_receive(self, client):
        while not client.should_stop:
            try:
                data = await client.readexactly(14)
            except ConnectionResetError:
                break
            except asyncio.IncompleteReadError:
                break

            self.push_data_to_send(data)

            if self.mirror_frames:
                for remote_client in self.clients.values():
                    if client == remote_client:
                        continue
                    remote_client.push_data_to_send(data)

        self.remove_client(client)

    # Handle sending data from ground station to client
    async def handle_client_send(self, client: ProxyClient):
        while not client.should_stop:
            if not client.send_queue:
                await asyncio.sleep(0)
                continue

            data = client.get_data_to_send()

            try:
                await client.write(data)
            except ConnectionResetError:
                break

        self.remove_client(client)

    # Handle new TCP client
    async def handle_new_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        client = self.add_client(reader, writer)
        asyncio.create_task(self.handle_client_receive(client))
        asyncio.create_task(self.handle_client_send(client))

    async def serve(self):
        self.open_transport()
        server = await asyncio.start_server(self.handle_new_client, self.tcp_address, self.tcp_port)
        asyncio.create_task(self.handle_station_receive())
        asyncio.create_task(self.handle_station_send())
        self._logger.info(
            f'Proxy active for serial port: {self.transport_settings.port}, '
            f'with baudrate: {self.transport_settings.baudrate}')
        self._logger.info(f'Listening for tcp connections on socket: {self.tcp_address}:{self.tcp_port}')
        async with server:
            await server.serve_forever()


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--tcp_address', required=True)
    parser.add_argument('--serial_port', required=True)
    parser.add_argument('--tcp_port', default=3000)
    parser.add_argument('--serial_baudrate', default=115200)
    parser.add_argument('--mirror_frames_to_clients', action='store_true')
    cl_args = parser.parse_args()
    proxy = Proxy()
    proxy.set_transport_options(SerialSettings(port=cl_args.serial_port, baudrate=cl_args.serial_baudrate))
    proxy.set_tcp_server_options(cl_args.tcp_address, cl_args.tcp_port)
    proxy.set_frame_mirroring(cl_args.mirror_frames_to_clients)
    asyncio.run(proxy.serve())
