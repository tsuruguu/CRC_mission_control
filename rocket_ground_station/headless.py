import os
import sys
import code
import logging
from logging import Logger
from typing import Dict, Tuple, Optional, List, Callable
from os.path import dirname, join
from datetime import datetime
from threading import Thread
from rocket_ground_station.core.communication import CommunicationManager
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.configs import HardwareConfig
from rocket_ground_station.core.communication.exceptions import (CommunicationError,
                                                                 ClosedTransportError,
                                                                 TransportTimeoutError)
# pylint: disable=global-statement,bare-except


def receive_loop(cm: CommunicationManager, logger: Logger):
    while True:
        if cm.is_connected:
            try:
                cm.receive()
            except TransportTimeoutError:
                pass
            except ClosedTransportError as error:
                logger.error(str(error) + '\nClosing the connection')
                cm.disconnect()
            except CommunicationError as error:
                logger.error(str(error))


def send_loop(cm: CommunicationManager, logger: Logger):
    while True:
        if cm.is_connected:
            try:
                cm.send()
            except (ClosedTransportError, TransportTimeoutError) as error:
                logger.error(str(error))
                logger.info('Closing the connection')
                cm.disconnect()
            except CommunicationError as error:
                logger.error(str(error))


def start_thread(target: Callable, args: tuple = None) -> Thread:
    receive_thread = Thread(target=target, args=args, daemon=True)
    receive_thread.start()


def create_connection(port: str,
                      logger: Logger,
                      baudrate: int = 115200,
                      timeout: int = 0,
                      write_timeout: Optional[int] = 1) -> CommunicationManager:
    cm = CommunicationManager()
    try:
        cm.connect(port, baudrate, timeout, write_timeout)
        logger.info(f'Established connection with {port}')
    except CommunicationError as error:
        logger.error(str(error))
    return cm


def create_devices(cm: CommunicationManager,
                   logger: Logger,
                   config_name: str = 'develop.yaml') -> List[Device]:
    config = HardwareConfig(config_name)
    if config.is_invalid:
        logger.error('Loaded invalid config: ' + config.error_message)
        return []
    device_msg = f'Loaded hardware config {config_name}:'
    for device_type, devices in config.as_dict().items():
        device_msg += f'\n\t{device_type}s: '
        device_msg += ', '.join(devices.keys())
    logger.info(device_msg)
    return [Device.from_type(device_type, name=device_name, communication=cm, **device_args)
            for device_type, device_name, device_args in config]


def initialize(port: str, logger: Logger) -> Tuple[CommunicationManager, List[Device]]:
    logger.info('Rocket Ground Station for AGH Space Systems 1.0.0')
    connection = create_connection(port, logger)
    start_thread(target=receive_loop, args=(connection, logger))
    start_thread(target=send_loop, args=(connection, logger))
    devices = create_devices(connection, logger)
    return connection, devices


COMMUNICATION: CommunicationManager = None
DEVICES: Dict[str, Device] = {}
LOGGER = logging.getLogger("main")
FORMAT = '[%(asctime)s] [%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.DEBUG)
file_handler = logging.FileHandler(
    join(dirname(__file__),
    'logs',
    str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S')) + ".log")
)
log_formatter = logging.Formatter(fmt=FORMAT)
file_handler.setFormatter(log_formatter)
LOGGER.addHandler(file_handler)



def setup_variables(port: str) -> None:
    global COMMUNICATION, DEVICES
    COMMUNICATION, DEVICES = initialize(port, LOGGER)
    device_variables = {}
    for device in DEVICES:
        device_type = str.lower(device.__class__.__name__) + 's'
        device_storage = device_variables.setdefault(
            device_type, type('DeviceStorage', (), {}))
        setattr(device_storage, device.name, device)
    globals().update(device_variables)


def on_exit() -> None:
    try:
        LOGGER.info('Closing the connection')
        COMMUNICATION.disconnect()
    except:
        pass
    raise SystemExit


def main() -> None:
    if len(sys.argv) > 1:
        port = sys.argv[1]
    elif os.environ.get('PORT'):
        port = os.environ.get('PORT')
    else:
        LOGGER.error('Please specify the port name as a first argument!')
        return
    setup_variables(port)
    code.interact(banner='', local={**globals(), **locals(), 'exit': on_exit, 'quit': on_exit})


if __name__ == '__main__':
    main()
