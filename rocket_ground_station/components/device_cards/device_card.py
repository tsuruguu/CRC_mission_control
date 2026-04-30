from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivymd.uix.card import MDCard
from kivy.metrics import dp  # pylint: disable=ungrouped-imports

from rocket_ground_station.components.device_cards.piston_card_content import PistonCard
from rocket_ground_station.components.device_widgets import DeviceWidget
from rocket_ground_station.components.device_cards.dynamixel_card_content import DynamixelCard
from rocket_ground_station.components.device_cards.flash_card_content import FlashCard
from rocket_ground_station.components.device_cards.igniter_card_content import IgniterCard
from rocket_ground_station.components.device_cards.relay_card_content import RelayCard
from rocket_ground_station.components.device_cards.recovery_card_content import RecoveryCard
from rocket_ground_station.components.device_cards.scheduler_card_content import SchedulerCard
from rocket_ground_station.components.device_cards.sensor_card_content import SensorCard
from rocket_ground_station.components.device_cards.servo_card_content import ServoCard
from rocket_ground_station.components.device_cards.supply_card_content import SupplyCard
from rocket_ground_station.components.device_cards.heating_lamp_card_content import HeatingLampCard
from rocket_ground_station.components.device_cards.multi_sensor_card_content import MultiSensorCard


class DeviceCard(MDCard):
    _implemented_cards = {
        'DynamixelWidget': DynamixelCard,
        'FlashWidget': FlashCard,
        'IgniterWidget': IgniterCard,
        'RelayWidget': RelayCard,
        'RecoveryWidget': RecoveryCard,
        'SchedulerWidget': SchedulerCard,
        'SensorWidget': SensorCard,
        'PistonWidget': PistonCard,
        'ServoWidget': ServoCard,
        'SupplyWidget': SupplyCard,
        'HeatingLampWidget': HeatingLampCard,
        'MultiSensorWidget': MultiSensorCard
    }
    device_widget: DeviceWidget = ObjectProperty(rebind=True)
    content = ObjectProperty()
    arm_button = ObjectProperty()
    synchronize_button = ObjectProperty()
    top_bar = ObjectProperty()

    def __init__(self, device_widget: DeviceWidget, com_tab, card_scale: float, **kwargs):
        super().__init__(**kwargs)
        self.device_widget = device_widget
        try:
            self.device_card = self._implemented_cards[device_widget.__class__.__name__](
                device_widget)
            self.content.add_widget(self.device_card)
        except KeyError:
            self.device_card = None
        device_widget.bind(is_synchronized=self.on_synchronize)
        device_widget.bind(is_device_armed=self.on_armed_state_change)

        if self.device_card is None:
            return

        self.disable()

        if self.device_card.requires_large_card:
            self.size = (dp(300), dp(350))

        if self.device_card.is_excluded_from_arming:
            self.top_bar.remove_widget(self.arm_button)

        if self.device_card.is_excluded_from_syncing:
            self.top_bar.remove_widget(self.synchronize_button)

        self.set_card_scaling(card_scale)

    def set_card_scaling(self, card_scale: float):
        self.size = (self.size[0] * card_scale, self.size[1] * card_scale)

    def on_synchronize(self, _instance, value) -> None:
        if value:
            # This self.disable() call is an ultra cursed method of redrawing the entire device card
            # Imagine that even after a synchronization,
            # values of open/closed_pos of servos and dynamixels won't update
            # even when you set rebind to True for the device widget
            # self.canvas.ask_update() and self.device_widget.ask_update() also don't work 0_0
            # self.content.canvas.ask_update() also doesn't do the job :/
            # Only after first disabling and then enabling the whole card again,
            # the new values are becoming visible
            if self.device_widget is not None:
                self.device_widget.handle_widget_refreshes()
            if self.device_card is not None:
                self.device_card.handle_widget_refreshes()
            self.disable()
            self.enable()

    def on_armed_state_change(self, _instance, is_device_armed) -> None:
        if is_device_armed:
            self.enable()
        else:
            self.disable()

    def enable(self, _caller: Widget = None) -> None:

        if self.device_card is None:
            return

        if self.device_card.is_excluded_from_arming:
            return

        self.device_card.disabled = False

    def disable(self, _caller: Widget = None) -> None:

        if self.device_card is None:
            return

        if self.device_card.is_excluded_from_arming:
            return

        self.device_card.disabled = True

    def _cycle_device_arm_state(self):
        if self.device_widget.is_device_armed:
            self.device_widget.disarm()
        else:
            self.device_widget.arm()

    @property
    def is_snapshottable(self) -> None:
        return self.device_widget.is_snapshottable

    @property
    def device_name(self) -> None:
        return self.device_widget.device_name
