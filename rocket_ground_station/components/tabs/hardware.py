from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty, StringProperty

from rocket_ground_station.core.communication import CommunicationManager
from rocket_ground_station.core.communication.mock_communication_manager import MockCommunicationManager
from rocket_ground_station.core.configs import HardwareConfig, AppConfig
from rocket_ground_station.core.devices import Device
from rocket_ground_station.components.device_widgets import (
    DeviceWidget, DynamixelWidget, ParachuteWidget, ResetWidget)
from rocket_ground_station.components.device_cards import DeviceCard
from rocket_ground_station.components.popups import Message, BinaryQuestion
from rocket_ground_station.core.communication.ids import LogLevel
from rocket_ground_station.components.tabs.tab import Tab
from rocket_ground_station.components.snapshot_manager import SnapshotManager
from typing import Union, Dict

from pathlib import Path
import sys

import subprocess
import platform

from rocket_ground_station.core.devices.dependency import Dependency

ALL_DEVICES_LABEL = "All devices"


class ViewProfile:
    """
        Represents single view profile used to display a specified group of devices.
    """

    def __init__(self, profile_name: str, device_names: Union[tuple[str], None]):
        self._profile_name = profile_name
        self._device_names = device_names

    @property
    def profile_name(self) -> str:
        return self._profile_name

    @property
    def device_names(self) -> tuple[str]:
        return self._device_names

    def __str__(self) -> str:
        return self._profile_name


class Hardware(Tab):
    """
    Implements a tab allowing user to create, load and edit hardware configurations.
    """
    dashboard = ObjectProperty()
    tab_title = ObjectProperty()
    snap_dropdown = ObjectProperty()
    maintenance_dropdown = ObjectProperty()
    view_profiles_dropdown = ObjectProperty()
    config_dropdown = ObjectProperty()
    config_folder_button = ObjectProperty()
    is_hardware_armed = BooleanProperty(False)
    recent_frames = StringProperty('')

    def __init__(self, cm: CommunicationManager, **tab_kwargs) -> None:
        super().__init__(**tab_kwargs)
        self._communication = cm
        self._device_cards = {}
        self._device_widgets_states = {}
        self._hardware_config = None
        self._view_profiles = None
        self._populate_config_dropdown()
        self._populate_snap_dropdown()
        self._populate_maintenance_dropdown()
        self.register_event_type('on_hardware_load')
        self._tabs['communication'].bind(on_connection_start=self.on_connection_start)
        self._tabs['communication'].frame_logger.logs.bind(text=self._get_recent_frames)
        self._logger.info('Hardware tab initialized')
        self.initialize_config_folder_button()
        self.snapshot_manager = SnapshotManager(
            current_devices=lambda: self.current_devices,
            snap_dropdown=self.snap_dropdown,
        )

    def _get_recent_frames(self, instance, text):
        self.recent_frames = '\n'.join(text.splitlines()[:5][::])

    def _populate_config_dropdown(self) -> None:
        self._populate_dropdown(HardwareConfig.get_all_config_names(), self.config_dropdown, 'code-json')

    def _populate_maintenance_dropdown(self) -> None:
        self.maintenance_dropdown.items = ['Reset Kromek']

    def _populate_snap_dropdown(self) -> None:
        self.snap_dropdown.items = ["Start snapshot", "Stop snapshot"]

    def load_hardware_config(self, config_name: str) -> None:
        config = HardwareConfig(config_name)
        if config.is_invalid:
            self._logger.error(f'Error: {config_name} is an invalid hardware config file '
                               f'{config.error_message}')
            Message.create(LogLevel.ERROR, f'{config_name} is an invalid hardware config file '
                                           f'{config.error_message}')
        else:
            self._communication.clear_callbacks()
            self._hardware_config = config
            device_widgets = self._create_device_widgets(config)
            view_profiles = self._create_view_profiles(config)
            self.dispatch('on_hardware_load', device_widgets, view_profiles)
            if isinstance(self._communication, MockCommunicationManager):
                self._communication.set_devices(device_widgets)

    #Button is only operational on Windows operating systems,
    # since Linux support would require handling too many different file managers and DEs
    def initialize_config_folder_button(self):
        if platform.system() != 'Windows':
            self.config_folder_button.disabled = True

    def open_hardware_config_folder(self) -> None:
        config_folder_path = Path(sys.argv[0]).resolve().parent.joinpath("configs/hardware_configs/")
        if config_folder_path.is_dir():
            try:
                subprocess.Popen(f'explorer "{config_folder_path}"')
            except subprocess.CalledProcessError as e:
                self._logger.error(f'Error opening folder: {e}')
        else:
            self._logger.error(f'Error: {config_folder_path} is not a valid directory')

    def _create_device_widgets(self, config: HardwareConfig) -> dict:
        devices = {device_name: Device.from_type(device_type,
                                                 name=device_name,
                                                 communication=self._communication,
                                                 **device_args)
                   for device_type, device_name, device_args in config}
        try:
            Dependency.load(devices)
        except (KeyError, TypeError) as e:
            self._logger.error(f'Error creating devices: {e}')
            Message.create(LogLevel.ERROR, f'Error creating devices: {e}')
            return {}

        # fill device widgets states
        return {device_name: DeviceWidget.from_device(devices[device_name]) for _, device_name, _ in config}

    def _create_view_profiles(self, config: HardwareConfig) -> list[ViewProfile]:
        view_profiles = [ViewProfile("All devices", None)]
        if hasattr(config, 'view_profiles'):
            for profile in config.view_profiles:
                view_profiles.append(ViewProfile(profile['profile_name'], profile['device_names']))
        return view_profiles

    def on_hardware_load(self, device_widgets: Dict[str, DeviceWidget],
                         view_profiles: list[ViewProfile]) -> None:
        # Load view profiles
        self._view_profiles = view_profiles
        self.view_profiles_dropdown.items = [vp.profile_name for vp in view_profiles]
        self.view_profiles_dropdown.text = view_profiles[0].profile_name
        self._logger.info('Loaded view profiles')
        # Load devices
        self._device_widgets = device_widgets
        self._refresh_dashboard()
        hardware = ' '.join(s.lower().capitalize()
                            for s in self.current_hardware.split('_'))
        self.tab_title.text = hardware + ' Rocket Hardware'
        self.config_dropdown.text = self.current_hardware.upper()
        self._logger.info(f'Loaded new hardware: {self.current_hardware}')
        self._tabs['communication'].on_hardware_load(device_widgets)
        if 'hydraulics' in self._tabs:
            self._tabs['hydraulics'].on_hardware_load(device_widgets)
        if 'sequences' in self._tabs:
            self._tabs['sequences'].on_hardware_load(device_widgets, self._hardware_config)
        if self._tabs['communication'].is_connected:
            self.on_connection_start(self)


    def _refresh_dashboard(self, text=None) -> None:
        if text is not None:
            self.view_profiles_dropdown.text = text
        devices = self._filter_profile_devices()

        device_cards = {}
        self.dashboard.clear_widgets()
        for device_widget in devices:
            device_cards[device_widget] = DeviceCard(
                device_widget, self._tabs['communication'], AppConfig().card_scale)
            self.dashboard.add_widget(device_cards[device_widget])
            if device_widget.is_device_armed:
                device_cards[device_widget].enable()
            else:
                device_cards[device_widget].disable()

    def execute_maintenance_option(self, option) -> None:
        if option == 'Reset Kromek':
            self.reset_board('KROMEK')
        else:
            raise ValueError(f'Unknown maintenance option provided: {option}')

    def _filter_profile_devices(self):
        if self.view_profiles_dropdown.text == ALL_DEVICES_LABEL:
            return list(self._device_widgets.values())

        def is_selected_profile(profile):
            return profile.profile_name == self.view_profiles_dropdown.text

        selected_profile = next(filter(is_selected_profile, self._view_profiles), None)
        if not selected_profile:
            return []

        devices = [device for device in self._device_widgets.values()
                   if device.name in selected_profile.device_names]

        return devices

    def execute_snap_option(self, option) -> None:
        if option == "Start snapshot":
            self.snapshot_manager.start_snapshotting()
            self.config_dropdown.disabled = True
            self.view_profiles_dropdown.disabled = True

        elif option == "Stop snapshot":
            self.snapshot_manager.stop_snapshotting()
            self.config_dropdown.disabled = False
            self.view_profiles_dropdown.disabled = False

    def on_connection_start(self, caller=None):
        """
        Called when connection is established.
        :param caller: widget that called the dispatched on_connection_start event
        """
        return

    def on_hardware_armed(self):
        """
        Called when all hardware is armed via ARM & SYNC button
        """
        self.sync_hardware()

    def sync_hardware(self, caller=None):
        if self.is_hardware_armed:
            for device_widget in self._device_widgets.values():
                device_widget.synchronize()

    def arm_hardware(self):
        def on_answer(disarm: bool):
            if not disarm:
                return
            self.is_hardware_armed = True
            for device_widget in self._device_widgets.values():
                device_widget.arm()
            self.on_hardware_armed()

        if not self._communication.is_connected:
            Message("No connection",
                    "Connection must be active in order to synchronize devices"
                    "\nPlease establish connection with the ground station before proceeding")
            return

        BinaryQuestion(question='Are you sure you want to arm the hardware?',
                       on_answer=on_answer)

    def disarm_hardware(self):
        self.is_hardware_armed = False
        for device_widget in self._device_widgets.values():
            device_widget.disarm()

    @staticmethod
    def _get_parachute_deployer(device_widgets: Dict[str, DeviceWidget]) -> ParachuteWidget:
        parachute_deployers = [device_widget for device_widget in device_widgets.values()
                               if isinstance(device_widget, ParachuteWidget)]
        return parachute_deployers[0] if len(parachute_deployers) > 0 else None

    def deploy_drogue(self) -> None:
        parachute_deployer = self._get_parachute_deployer(self._device_widgets)
        if parachute_deployer is not None:
            parachute_deployer.drogue()

    def deploy_main(self) -> None:
        parachute_deployer = self._get_parachute_deployer(self._device_widgets)
        if parachute_deployer is not None:
            parachute_deployer.main()

    def reset_dynamixels(self) -> None:
        for device_widget in self._device_widgets.values():
            if isinstance(device_widget, DynamixelWidget):
                if not device_widget.is_device_armed:
                    device_widget.arm()
                device_widget.reset()
        Clock.schedule_once(self._sync_dynamixels, AppConfig().dynamixel_reset_sync_delay)

    def reset_board(self, board: str) -> None:
        for device_widget in self._device_widgets.values():
            if isinstance(device_widget, ResetWidget):
                if board == device_widget.board_name:
                    device_widget.reset()
                    return
        Message('Reset device not found', f'No "Reset" Device was found for the requested board: {board}'
                f'\nPlease add it to the hardware configuration file.')

    def _sync_dynamixels(self, dt) -> None:
        for device_widget in self._device_widgets.values():
            if isinstance(device_widget, DynamixelWidget):
                device_widget.synchronize()

    @property
    def current_hardware(self) -> str:
        """
        Returns the name of the currently used hardware config file.
        """
        return self._hardware_config.name if self._hardware_config is not None else str(None)

    @property
    def current_devices(self) -> dict:
        """
        Returns dict of current devices
        """
        return self._device_widgets
