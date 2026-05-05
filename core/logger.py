import logging
import csv
import time
from datetime import datetime
from pathlib import Path
from core.data_types import TelemetryFrame


class DPGHandler(logging.Handler):
    """Specjalny handler przesyłający logi systemowe do terminala w Dear PyGui."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        # Przekazanie sformatowanego tekstu do komponentu UI[cite: 4, 9]
        if self.callback:
            self.callback(log_entry, record.levelno)


class MissionLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        # Unikalny identyfikator sesji zapobiega nadpisywaniu danych[cite: 4]
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.telemetry_file = self.log_dir / f"telemetry_{self.session_id}.csv"
        self.system_file = self.log_dir / f"system_{self.session_id}.log"

        self._setup_system_logger()
        self._setup_csv_header()

    def _setup_system_logger(self):
        """Konfiguracja loggera dla zdarzeń systemowych, błędów i ostrzeżeń[cite: 4]."""
        self.logger = logging.getLogger("MissionControl")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )

        # Logowanie do pliku tekstowego[cite: 4]
        file_handler = logging.FileHandler(self.system_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Logowanie do konsoli programisty[cite: 4]
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_csv_header(self):
        """Inicjalizacja nagłówków CSV zgodnie z modelem TelemetryFrame."""
        headers = [
            "timestamp", "frame_id", "state",
            "acc_x", "acc_y", "acc_z",
            "gyr_x", "gyr_y", "gyr_z",
            "mag_x", "mag_y", "mag_z",
            "alt", "lat", "lon", "temp",
            "volt", "curr", "strain",
            "pitch", "roll", "yaw"
        ]
        with open(self.telemetry_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def log_telemetry(self, frame: TelemetryFrame):
        """Zapisuje kompletną ramkę danych do pliku CSV dla analizy post-flight[cite: 4, 5]."""
        try:
            with open(self.telemetry_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    time.time(),
                    frame.frame_id,
                    frame.state.value,
                    frame.accel.x, frame.accel.y, frame.accel.z,
                    frame.gyro.x, frame.gyro.y, frame.gyro.z,
                    frame.mag.x, frame.mag.y, frame.mag.z,
                    frame.altitude,
                    frame.latitude,
                    frame.longitude,
                    frame.temp,
                    frame.voltage,
                    frame.current,
                    frame.strain_gauge,
                    frame.pitch,
                    frame.roll,
                    frame.yaw
                ])
        except Exception as e:
            self.error(f"Krytyczny błąd zapisu telemetrii: {e}")

    # Standardowe metody logowania systemowego[cite: 4]
    def info(self, msg): self.logger.info(msg)
    def debug(self, msg): self.logger.debug(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def critical(self, msg): self.logger.critical(msg)

    def add_ui_handler(self, callback):
        """Umożliwia przekazywanie logów do okna Ground Station Logs w czasie rzeczywistym[cite: 4, 9]."""
        handler = DPGHandler(callback)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)