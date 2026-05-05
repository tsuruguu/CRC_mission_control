from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class RocketState:
    # Dane podstawowe (zgodnie z raportem FST AGH)
    timestamp: float = 0.0
    frame_id: int = 0
    mission_state: str = "IDLE"  # IDLE, LAUNCH, ASCENT, APOGEE, DESCENT, LANDING

    # Orientacja i Dynamika (IMU + Altimeter)
    accel: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    gyro: list = field(default_factory=lambda: [0.0, 0.0, 0.0])
    pressure: float = 101325.0
    altitude: float = 0.0

    # GPS
    lat: float = 0.0
    lon: float = 0.0

    # Hardware & Bio (AstroBio Payload)
    temp: float = 20.0
    voltage: float = 0.0
    current: float = 0.0
    strain_gauge: float = 0.0

    # Diagnostyka połączenia
    last_update: float = field(default_factory=time.time)
    dropped_frames: int = 0


class TelemetryParser:
    def __init__(self):
        self.state = RocketState()
        self._last_frame_id = -1

    def parse_line(self, line: str) -> Optional[RocketState]:
        """
        Zakładamy format CSV wysyłany przez STM32:
        ID;STATE;ACC_X;ACC_Y;ACC_Z;GYR_X;GYR_Y;GYR_Z;ALT;LAT;LON;TEMP;VOLT
        """
        try:
            parts = line.split(';')
            if len(parts) < 10:
                return None

            f_id = int(parts[0])

            # Logika żółtego LED-a: Sprawdzanie ciągłości ramek
            if self._last_frame_id != -1 and f_id != self._last_frame_id + 1:
                self.state.dropped_frames += (f_id - self._last_frame_id - 1)

            self._last_frame_id = f_id

            # Mapowanie danych
            self.state.frame_id = f_id
            self.state.mission_state = parts[1]
            self.state.accel = [float(parts[2]), float(parts[3]), float(parts[4])]
            self.state.gyro = [float(parts[5]), float(parts[6]), float(parts[7])]
            self.state.altitude = float(parts[8])
            self.state.lat = float(parts[9])
            self.state.lon = float(parts[10])
            self.state.temp = float(parts[11])
            self.state.voltage = float(parts[12])

            self.state.last_update = time.time()
            self.state.timestamp = time.time()

            return self.state
        except (ValueError, IndexError):
            # Tu wchodzi status BLUE (dane terminala / błąd formatu)
            return None

    def get_connection_status(state: RocketState) -> str:
        """
        Zwraca kolor statusu na podstawie danych:
        - BLACK: Brak połączenia
        - RED: Błąd (np. krytyczne napięcie)
        - GREEN: Wszystko sprawne
        - YELLOW: Utrata ramek
        - BLUE: Dane terminala (aktywność RX)
        """
        time_since_last = time.time() - state.last_update

        if time_since_last > 2.0:
            return "BLACK"  # Timeout
        if state.voltage < 3.3:  # Przykładowy błąd hardware
            return "RED"
        if state.dropped_frames > 0:
            # Możesz zresetować licznik po pewnym czasie, żeby LED wrócił na zielony
            return "YELLOW"
        return "GREEN"