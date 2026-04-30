from functools import partial

from kivy.properties import BooleanProperty, DictProperty
from kivy.uix.widget import Widget

from rocket_ground_station.core.communication.ids import AckStatus
from rocket_ground_station.core.communication import ids
from rocket_ground_station.core.devices import Device
from rocket_ground_station.core.exceptions import DeviceWidgetNotImplementedError


class DeviceWidget(Widget):
    """
    Implements generic device interaction layer
    """
    ack_states = DictProperty({})
    is_synchronized = BooleanProperty(defaultvalue=False)
    is_device_armed = BooleanProperty(defaultvalue=False)
    has_attempted_synchronization = BooleanProperty(defaultvalue=False)
    is_synchronization_ongoing = BooleanProperty(defaultvalue=False)

    implemented_widgets = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls.type_id = ids.DeviceID[str.upper(cls.__name__)[:-6]]
        cls._ids = ids.OperationID[str.upper(cls.__name__)[:-6]].value
        DeviceWidget.implemented_widgets[str.lower(cls.__name__)] = cls

    @staticmethod
    def from_device(device: Device):
        device_type = str.lower(device.__class__.__name__)
        try:
            return DeviceWidget.implemented_widgets[device_type+"widget"](device)
        except KeyError:
            raise DeviceWidgetNotImplementedError(
                f'Failed to create a device with type: {device_type+"widget"}')

    def __init__(self, device: Device, **kwargs):
        super().__init__(**kwargs)
        self._device = device
        self.register_event_type('on_synchronize')

    def synchronize(self) -> None:
        self.arm()
        self.is_synchronized = False
        self.has_attempted_synchronization = True
        self.is_synchronization_ongoing = True
        self._device.synchronize(on_synchronize=partial(
            self.dispatch, 'on_synchronize'))

    def on_synchronize(self):
        self.is_synchronized = True
        self.is_synchronization_ongoing = False

    def arm(self):
        self.is_device_armed = True
        for action_name in self.ack_states:
            self.ack_states[action_name] = AckStatus.READY
        self._device.arm()

    def disarm(self):
        self.is_device_armed = False
        for action_name in self.ack_states:
            self.ack_states[action_name] = AckStatus.DISABLED
        self._device.disarm()

    def reset_ack_states(self):
        for key in self.ack_states:
            self.ack_states[key] = AckStatus.READY

    def handle_widget_refreshes(self):
        pass

    @property
    def board(self) -> int:
        return self._device.board

    @property
    def board_name(self) -> str:
        return self._device.board_name

    @property
    def device_type(self) -> str:
        return type(self._device).__name__

    @property
    def id(self) -> int:
        return self._device.id

    @property
    def name(self) -> str:
        return self._device.name

    @property
    def is_snapshottable(self) -> bool:
        return self._device.is_snapshottable

    @property
    def service_ids(self) -> tuple:
        return self._device.service_ids

    @property
    def request_ids(self) -> tuple:
        return self._device.request_ids

    @property
    def feed_ids(self) -> tuple:
        return self._device.feed_ids

    def as_device(self) -> Device:
        return self._device

    def __str__(self) -> str:
        return self.__class__.__name__
