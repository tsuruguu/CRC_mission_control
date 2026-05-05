import time
from typing import Optional
from core.data_types import TelemetryFrame, MissionState, ConnectionStatus, Vector3


class TelemetryParser:
    def __init__(self):
        self.state = TelemetryFrame()
        self._last_frame_id = -1
        self._last_valid_time = 0.0

    def parse_line(self, line: str) -> Optional[TelemetryFrame]:
        """
        Parsuje linię CSV z STM32. 
        Format: ID;STATE;ACC_X;ACC_Y;ACC_Z;GYR_X;GYR_Y;GYR_Z;MAG_X;MAG_Y;MAG_Z;ALT;LAT;LON;TEMP;VOLT;CURR;STRAIN;P;R;Y
        """
        try:
            parts = line.split(';')
            # Minimalna liczba elementów (bazując na raporcie avioniki[cite: 1])
            if len(parts) < 15:
                return None

            f_id = int(parts[0])

            # 1. Logika ciągłości (Żółty LED)
            if self._last_frame_id != -1 and f_id != self._last_frame_id + 1:
                dropped = f_id - self._last_frame_id - 1
                if dropped > 0:
                    self.state.dropped_frames += dropped

            self._last_frame_id = f_id

            # 2. Mapowanie danych systemowych[cite: 1]
            self.state.frame_id = f_id
            try:
                self.state.state = MissionState(parts[1])
            except ValueError:
                self.state.state = MissionState.IDLE

            # 3. Dynamika (IMU 9-axis)[cite: 1]
            self.state.accel = Vector3(float(parts[2]), float(parts[3]), float(parts[4]))
            self.state.gyro = Vector3(float(parts[5]), float(parts[6]), float(parts[7]))
            self.state.mag = Vector3(float(parts[8]), float(parts[9]), float(parts[10]))

            # 4. Wysokość i GPS[cite: 1]
            self.state.altitude = float(parts[11])
            self.state.latitude = float(parts[12])
            self.state.longitude = float(parts[13])

            # 5. Hardware & Payload[cite: 1]
            self.state.temp_payload = float(parts[14])
            self.state.voltage = float(parts[15])
            self.state.current = float(parts[16])
            self.state.strain_gauge = float(parts[17])

            # 6. Orientacja dla Navballa (Pitch, Roll, Yaw)[cite: 1]
            self.state.pitch = float(parts[18])
            self.state.roll = float(parts[19])
            self.state.yaw = float(parts[20])

            # Aktualizacja diagnostyki
            self._last_valid_time = time.time()
            self.state.last_update = self._last_valid_time
            self.state.timestamp = self._last_valid_time

            return self.state

        except (ValueError, IndexError):
            # Błąd formatu oznacza status BLUE (aktywność terminala / śmieci)[cite: 2]
            return None

    def get_connection_status(self) -> ConnectionStatus:
        """
        Zwraca status połączenia na podstawie czasu i jakości danych[cite: 2].
        """
        now = time.time()
        time_since_last = now - self._last_valid_time

        # BLACK: Brak danych powyżej 2 sekund[cite: 2]
        if time_since_last > 2.0:
            return ConnectionStatus.DISCONNECTED

        # RED: Błąd zasilania (krytyczne dla 18650)[cite: 1, 2]
        if self.state.voltage > 0 and self.state.voltage < 3.3:
            return ConnectionStatus.ERROR

        # YELLOW: Wykryto brakujące ramki w bieżącej sesji[cite: 2]
        if self.state.dropped_frames > 0:
            return ConnectionStatus.DROPPED_FRAMES

        # GREEN: Wszystko sprawne[cite: 2]
        return ConnectionStatus.CONNECTED