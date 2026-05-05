import time
import logging
from typing import Optional
from core.data_types import TelemetryFrame, MissionState, ConnectionStatus, Vector3

class TelemetryParser:
    def __init__(self):
        """Inicjalizacja parsera z czystym stanem i loggerem systemowym."""
        self.state = TelemetryFrame()
        self._last_frame_id = -1
        self._last_valid_time = 0.0
        self.logger = logging.getLogger("MissionControl")
        self._prev_mission_state = MissionState.IDLE
        self._prev_conn_status = ConnectionStatus.DISCONNECTED

    def parse_line(self, line: str) -> Optional[TelemetryFrame]:
        """
        Parsuje linię CSV z STM32 i zarządza logiką diagnostyczną.
        Format ramki: ID;STATE;ACC_X;ACC_Y;ACC_Z;GYR_X;GYR_Y;GYR_Z;MAG_X;MAG_Y;MAG_Z;ALT;LAT;LON;TEMP;VOLT;CURR;STRAIN;P;R;Y
        """
        try:
            parts = line.split(';')
            # Minimalna liczba elementów (bazując na raporcie avioniki[cite: 1])
            if len(parts) < 15:
                return None

            f_id = int(parts[0])

            # 1. Logika ciągłości (Żółty LED - Dropped Frames)[cite: 25]
            if self._last_frame_id != -1 and f_id != self._last_frame_id + 1:
                dropped = f_id - self._last_frame_id - 1
                if dropped > 0:
                    self.state.dropped_frames += dropped
                    self.logger.warning(
                        f"Luka w telemetrii: zgubiono {dropped} ramek. Razem: {self.state.dropped_frames}"
                    )

            self._last_frame_id = f_id

            # 2. Mapowanie stanu misji i logowanie przejść FSM
            self.state.frame_id = f_id
            try:
                new_state = MissionState(parts[1])
                if new_state != self._prev_mission_state:
                    self.logger.info(f"Zmiana stanu rakiety: {self._prev_mission_state.value} -> {new_state.value}")
                    self._prev_mission_state = new_state
                self.state.state = new_state
            except ValueError:
                self.state.state = MissionState.IDLE

            # 3. Dynamika lotu (IMU 9-osiowe)[cite: 1]
            self.state.accel = Vector3(float(parts[2]), float(parts[3]), float(parts[4]))
            self.state.gyro = Vector3(float(parts[5]), float(parts[6]), float(parts[7]))
            self.state.mag = Vector3(float(parts[8]), float(parts[9]), float(parts[10]))

            # 4. Wysokość i Pozycjonowanie GPS[cite: 1]
            self.state.altitude = float(parts[11])
            self.state.latitude = float(parts[12])
            self.state.longitude = float(parts[13])

            # 5. Hardware & Bio-Payload[cite: 1]
            self.state.temp_payload = float(parts[14])
            self.state.voltage = float(parts[15])
            self.state.current = float(parts[16])
            self.state.strain_gauge = float(parts[17])

            # 6. Orientacja dla Navballa (Pitch, Roll, Yaw)[cite: 1, 13]
            self.state.pitch = float(parts[18])
            self.state.roll = float(parts[19])
            self.state.yaw = float(parts[20])

            # Aktualizacja timestampów diagnostycznych
            self._last_valid_time = time.time()
            self.state.last_update = self._last_valid_time
            self.state.timestamp = self._last_valid_time

            return self.state

        except (ValueError, IndexError) as e:
            # Rejestrowanie błędów transmisji/parsowania jako status BLUE w terminalu[cite: 2, 25]
            self.logger.error(f"Błąd parsowania linii: '{line}'. Szczegóły: {e}")
            return None

    def get_connection_status(self) -> ConnectionStatus:
        """
        Oblicza status połączenia i loguje tylko zmiany stanów (NASA standard)[cite: 2, 25].
        """
        now = time.time()
        time_since_last = now - self._last_valid_time

        # 1. Określenie bieżącego statusu[cite: 2, 25]
        if time_since_last > 2.0:
            current_status = ConnectionStatus.DISCONNECTED  # BLACK[cite: 2]
        elif self.state.voltage > 0 and self.state.voltage < 3.3:
            current_status = ConnectionStatus.ERROR  # RED[cite: 1, 25]
        elif self.state.dropped_frames > 0:
            current_status = ConnectionStatus.DROPPED_FRAMES  # YELLOW[cite: 2, 25]
        else:
            current_status = ConnectionStatus.CONNECTED  # GREEN[cite: 2]

        # 2. Logowanie przejść między stanami (wykonuje się tylko raz przy zmianie)[cite: 25]
        if current_status != self._prev_conn_status:
            if current_status == ConnectionStatus.DISCONNECTED:
                self.logger.error(f"UTTRATA SYGNAŁU: Brak danych od {time_since_last:.1f}s")

            elif current_status == ConnectionStatus.ERROR:
                self.logger.critical(f"BŁĄD ZASILANIA: Napięcie spadło do {self.state.voltage:.2f}V!")

            elif current_status == ConnectionStatus.DROPPED_FRAMES:
                self.logger.warning(
                    f"DEGRADACJA LINKU: Wykryto luki w transmisji LoRa (Suma: {self.state.dropped_frames})")

            elif current_status == ConnectionStatus.CONNECTED:
                # Logujemy powrót do normy, jeśli poprzednio był błąd lub rozłączenie[cite: 25]
                if self._prev_conn_status in [ConnectionStatus.DISCONNECTED, ConnectionStatus.ERROR]:
                    self.logger.info("POŁĄCZENIE ODZYSKANE: Link telemetrii stabilny")

            # Aktualizacja poprzedniego stanu[cite: 25]
            self._prev_conn_status = current_status

        return current_status