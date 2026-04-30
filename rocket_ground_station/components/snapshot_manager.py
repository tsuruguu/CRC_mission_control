from kivy.event import EventDispatcher

from datetime import datetime
from math import floor
from queue import PriorityQueue
from threading import Thread
from bisect import bisect_left
from pandas import DataFrame, Series
from pathlib import Path
from os.path import join
from rocket_ground_station.components.device_widgets import (
    SensorWidget, DynamixelWidget)

import sys

from rocket_ground_station.core.configs import AppConfig


class SnapshotManager(EventDispatcher):
    """
    A UI component for managing snapshots in the Hardware tab.
    """

    def __init__(self, current_devices, snap_dropdown, **kwargs):
        super().__init__(**kwargs)
        self.get_device_widgets = current_devices
        self.snap_dropdown = snap_dropdown
        self._snapshot_info = self._create_snapshot_dict()
        self._snapshotting_now = False
        self._snapshotting_start = 0

    def _create_snapshot_dict(self) -> dict:
        snapshot_dict = {}
        for device_widget in self.get_device_widgets().values():
            if device_widget.is_snapshottable:
                snapshot_dict[device_widget.name] = PriorityQueue()
        return snapshot_dict

    def start_snapshotting(self) -> None:
        if self._snapshotting_now:
            return

        self.purge_snapshots()

        device_widgets = self.get_device_widgets().values()
        self._snapshotting_start = datetime.timestamp(datetime.now())

        for device_widget in device_widgets:
            # currently only implemented for SensorWidgets and PistonWidgets
            if device_widget.is_snapshottable:
                if isinstance(device_widget, SensorWidget):
                    self.value_snapshotted(device_widget, device_widget.rounded_value)
                    device_widget.bind(rounded_value=self.value_snapshotted)
                elif isinstance(device_widget, DynamixelWidget):
                    self.value_snapshotted(device_widget, device_widget.position)
                    device_widget.bind(position=self.value_snapshotted)

        self.snap_dropdown.text = "Snapshot ongoing!"
        self._snapshotting_now = True

    def value_snapshotted(self, instance, rounded_value) -> None:
        now_timestamp = int(datetime.timestamp(datetime.now())) * 1e6
        self._snapshot_info[instance.name].put((now_timestamp, rounded_value))

    def purge_snapshots(self) -> None:
        self._snapshot_info = {}
        self._snapshot_info = self._create_snapshot_dict()

    def unix_to_datetime(self, timestamp) -> datetime:
        return datetime.fromtimestamp(int(timestamp) / 1e6)

    def stop_snapshotting(self) -> None:
        if self.should_save_snapshot():
            for device_widget in self.get_device_widgets().values():
                # currently only implemented for SensorWidgets and PistonWidgets
                if device_widget.is_snapshottable:
                    if isinstance(device_widget, SensorWidget):
                        device_widget.unbind(rounded_value=self.value_snapshotted)
                    elif isinstance(device_widget, DynamixelWidget):
                        device_widget.unbind(position=self.value_snapshotted)

            saving_thread = Thread(target=self.save_snapshot)
            saving_thread.start()

    def should_save_snapshot(self) -> bool:
        if not self._snapshotting_now:
            return False

        # stop without operations if snapshot is empty
        if all(len(self._snapshot_info[key].queue) == 0 for key in self._snapshot_info):
            self.purge_snapshots()
            self.snap_dropdown.text = "Snapshot idle"
            self._snapshotting_now = False
            return False

        return True

    def save_snapshot(self) -> None:

        self.snap_dropdown.text = "Saving snapshot..."
        starttime = self._snapshotting_start
        endtime = datetime.timestamp(datetime.now())
        interval_length = AppConfig().snapshot_step_interval
        intervals_amount = floor((endtime - starttime) / interval_length)

        # converting from miliseconds to seconds
        measurement_points = [(starttime + (i * interval_length)) * 1e6 for i in range(intervals_amount)]
        measurement_points.append(endtime * 1e6)

        def closest_val_by_timestamp(queue, timestamp):
            point = bisect_left([qtimestamp for qtimestamp, val in queue], timestamp)
            return queue[point - 1][1]

        fixed_interval_dict = {k: PriorityQueue() for k in self._snapshot_info.keys()}
        for key, snap_queue in self._snapshot_info.items():
            for point in measurement_points:
                fixed_interval_dict[key].put((point, closest_val_by_timestamp(snap_queue.queue, point)))

        self._snapshot_info = {key: fixed_interval_dict[key].queue for key in fixed_interval_dict}

        df = DataFrame({k: Series(v) for k, v in self._snapshot_info.items()})
        df.fillna(method='ffill', inplace=True)

        def index_mapper(row):
            latest_update_date = max(df.loc[row].values, key=lambda x: x[0])[0]
            date = self.unix_to_datetime(latest_update_date)
            return date

        df.rename(index=index_mapper, inplace=True)
        df = df.map(lambda x: round(x[1], 3))
        current_time = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
        path = Path(sys.argv[0]).resolve().parent.joinpath('logs').joinpath('snapshots')
        Path(path).mkdir(parents=True, exist_ok=True)
        df.to_csv(join(path, f'{current_time}.csv'))

        self.purge_snapshots()
        self._snapshotting_now = False
        self.snap_dropdown.text = "Snapshot idle"
