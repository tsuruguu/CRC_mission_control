import os

from rocket_ground_station.core.communication.serial_transport import SerialSettings
from rocket_ground_station.core.communication.transport import TransportType
from rocket_ground_station.core.communication import CommunicationManager
from rocket_ground_station.core.communication.exceptions import UnregisteredCallbackError

if os.getenv("USE_RUST") and os.getenv("USE_RUST").lower() == "true":
    from python_sw_core.communication.exceptions import TransportTimeoutError # pylint: disable=import-error
else:
    from rocket_ground_station.core.communication.exceptions import TransportTimeoutError # pylint: disable=ungrouped-imports

from time import perf_counter


class BenchmarkReceiver:
    def run(self):
        manager = CommunicationManager()
        manager.change_transport_type(TransportType.SERIAL)
        counter = 0
        target = 30000
        manager.connect(SerialSettings(port='COM6', baudrate=115200))
        start_time = perf_counter()
        while counter < target:
            try:
                _frame = manager.receive()
            except UnregisteredCallbackError:
                pass
            except TransportTimeoutError:
                continue
            counter = counter + 1
        end_time = perf_counter()
        diff = end_time - start_time
        print(f'start time: {start_time}, '
              f'end time: {end_time}, '
              f'diff: {diff}, '
              f'frame per second: {target / diff}')


if __name__ == '__main__':
    BenchmarkReceiver().run()
