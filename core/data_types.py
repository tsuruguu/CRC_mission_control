from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple


class MissionState(Enum):
    """Stany misji zgodnie z dokumentacją FSM rakiety"""
    IDLE = "IDLE"  # Oczekiwanie, buzzer miga
    LAUNCH = "LAUNCH"  # Wykryto start (przeciążenie)[cite: 1]
    ASCENT = "ASCENT"  # Lot w górę, aktywny PID[cite: 1]
    APOGEE = "APOGEE"  # Detekcja szczytu, wyrzut spadochronu[cite: 1]
    DESCENT = "DESCENT"  # Opadanie pod spadochronem[cite: 1]
    LANDING = "LANDING"  # Przyziemienie, buzzer lokalizacyjny[cite: 1]
    EMERGENCY = "EMERGENCY"  # Ręczne wyzwolenie procedur bezpieczeństwa


class ConnectionStatus(Enum):
    """Logika LED opisana w Twoim projekcie[cite: 1]"""
    DISCONNECTED = (0, 0, 0)  # BLACK
    CONNECTED = (0, 255, 0)  # GREEN
    ERROR = (255, 0, 0)  # RED
    DROPPED_FRAMES = (255, 191, 0)  # YELLOW (Amber)
    DATA_RECEIVING = (0, 0, 255)  # BLUE (Terminal activity)


@dataclass
class Vector3:
    """Pomocniczy typ dla danych z IMU (9-osiowe)[cite: 1]"""
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0

    def to_tuple(self) -> Tuple[float, float, float]:
        return (self.x, self.y, self.z)


@dataclass
class TelemetryFrame:
    """
    Pełny model danych rakiety.
    Zawiera wszystkie sensory wymienione w sekcji Avionics[cite: 1].
    """
    # Systemowe
    frame_id: int = 0
    timestamp: float = 0.0
    state: MissionState = MissionState.IDLE

    # Dynamika lotu (IMU + Altimeter)[cite: 1]
    accel: Vector3 = field(default_factory=Vector3)
    gyro: Vector3 = field(default_factory=Vector3)
    mag: Vector3 = field(default_factory=Vector3)
    pressure: float = 1013.25
    altitude: float = 0.0

    # Nawigacja[cite: 1]
    latitude: float = 0.0
    longitude: float = 0.0

    # Hardware & Payload[cite: 1]
    temp_payload: float = 20.0
    voltage: float = 0.0  # Czujnik napięcia baterii 18650[cite: 1]
    current: float = 0.0  # Czujnik prądu[cite: 1]
    strain_gauge: float = 0.0  # Tensometry monitorujące konstrukcję[cite: 1]

    # Orientacja dla Navballa
    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0


@dataclass
class UIConfig:
    """Ustawienia interfejsu (kolory Skylink AGH)[cite: 1]"""
    bg_color: Tuple[int, int, int] = (11, 14, 20)  # #0B0E14
    accent_color: Tuple[int, int, int] = (0, 168, 150)  # #00A896
    text_color: Tuple[int, int, int] = (224, 224, 224)  # #E0E0E0

    # Statusy terminala
    autoscroll: bool = True
    show_timestamps: bool = True