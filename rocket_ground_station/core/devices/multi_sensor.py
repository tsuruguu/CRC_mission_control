from rocket_ground_station.core.devices.dependency import Dependency, SharedListVariable
from rocket_ground_station.core.devices.sensor import Sensor

class MultiSensor(Sensor, Dependency):
    """
    Implements a sensor device that can obtain and process values from multiple other sensors.
    Made specifically for gathering data from multiple tensometers at the same time,
    but can be also made useful for other purposes.

    All sensor are expected to have the same units.
    Moreover, each sensor can be individually calibrated, but in case it's not favorable
    their respective "a" and "b" values can be set to a=1 and b=0.
    And then the resulting output can be calibrated using the a and b of this device.
    """
    def __init__(self,
                 dependencies=None,
                 **sensor_kwargs):
        super().__init__(**sensor_kwargs)
        Dependency.__init__(self, dependencies)
        self._aggregate = SharedListVariable('aggregate',
                                             self._update_sensor_value)

    def _on_value_received(self, value: float):
        # Override to prevent updating the sensor directly
        pass

    def _update_sensor_value(self):
        aggregated_value = self._aggregation_function(self._aggregate.get())
        super()._on_value_received(aggregated_value)

    def _aggregation_function(self, values: list[float]) -> float:
        return sum(values)
