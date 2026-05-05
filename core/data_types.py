from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class MissionState(Enum):
    """Stany automatu FSM rakiety zgodnie z raportem FST AGH."""
    IDLE = "IDLE"  # Oczekiwanie, buzzer miga (0.5s on, 5s off)[cite: 1]
    LAUNCH = "LAUNCH"  # Wykryto przeciążenie startowe[cite: 1]
    ASCENT = "ASCENT"  # Lot w górę, aktywny algorytm PID[cite: 1]
    APOGEE = "APOGEE"  # Detekcja szczytu, wyrzut spadochronu[cite: 1]
    DESCENT = "DESCENT"  # Kontrolowane opadanie[cite: 1]
    LANDING = "LANDING"  # Przyziemienie, buzzer lokalizacyjny[cite: 1]
    EMERGENCY = "EMERGENCY"  # Ręczne wymuszenie procedur bezpieczeństwa


class ConnectionStatus(Enum):
    """Kolory statusu LED zgodnie z wymaganiami projektowymi[cite: 2]."""
    DISCONNECTED = (0, 0, 0)  # BLACK: Brak połączenia / Reset[cite: 2]
    CONNECTED = (0, 255, 0)  # GREEN: Wszystko sprawne[cite: 2]
    ERROR = (255, 0, 0)  # RED: Błąd krytyczny (np. niskie napięcie)[cite: 2]
    DROPPED_FRAMES = (255, 191, 0)  # YELLOW: Brak ciągłości ramek (zasięg)[cite: 2]
    DATA_RECEIVING = (0, 0, 255)  # BLUE: Aktywność terminala / Dane RX[cite: 2]


@dataclass
class Vector3:
    """Typ pomocniczy dla sensorów 3-osiowych (IMU)[cite: 1]."""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class TelemetryFrame:
    """
    Pełny model danych rakiety.
    Zawiera parametry wszystkich modułów: Avionics, AstroBio i ThrustLab[cite: 1].
    """
    # Dane systemowe
    frame_id: int = 0
    timestamp: float = 0.0
    state: MissionState = MissionState.IDLE

    # Dynamika i Orientacja (9-osiowe IMU + Barometr)[cite: 1]
    accel: Vector3 = field(default_factory=Vector3)
    gyro: Vector3 = field(default_factory=Vector3)
    mag: Vector3 = field(default_factory=Vector3)
    pressure: float = 101325.0
    altitude: float = 0.0

    # Pozycjonowanie (GPS GP-02)[cite: 1]
    latitude: float = 0.0
    longitude: float = 0.0

    # Parametry Hardware i Bio-Payload[cite: 1]
    temp: float = 20.0  # Temperatura (Payload monitoring)[cite: 1]
    voltage: float = 0.0  # Napięcie baterii 18650[cite: 1]
    current: float = 0.0  # Czujnik prądu[cite: 1]
    strain_gauge: float = 0.0  # Obciążenia konstrukcji (tensometry)[cite: 1]

    # Orientacja dla Navballa (obliczona fuzja czujników)
    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0

    # Diagnostyka stacji
    last_update: float = field(default_factory=lambda: 0.0)
    dropped_frames: int = 0