from rocket_ground_station.components.device_widgets.sensor_widget import SensorWidget
from rocket_ground_station.core.devices.multi_sensor import MultiSensor


class MultiSensorWidget(SensorWidget):
    _device: MultiSensor
