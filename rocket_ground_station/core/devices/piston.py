from rocket_ground_station.core.devices.sensor import Sensor


class Piston(Sensor):
    """
    Implements a sensor with minimum and maximum value,
    allowing for visual representation of piston position in a tank implemented in piston_widget
    treated as Sensor by the communication protocol

    Allows for specifying the volume and length units separately, and 
    """
    def __init__(self, min_val: float,
                 max_val: float,
                 volume: float,
                 length: float,
                 length_units: str = 'mm',
                 volume_units: str = 'ml',
                 display_volume: bool = True,
                 display_length: bool = True,
                 max_percentage_safe_val: float = 100,
                 min_percentage_safe_val: float = 40,
                 show_fuel_volume: bool = False,
                 **sensor_kwargs):
        super().__init__(**sensor_kwargs)
        self.max = max_val
        self.min = min_val
        self.lenunit = length_units
        self.volunit = volume_units
        self.vol = volume
        self.len = length
        self.isvol = display_volume
        self.islen = display_length
        self.maxsafe = max_percentage_safe_val
        self.minsafe = min_percentage_safe_val
        self.show_fuel_volume = show_fuel_volume
