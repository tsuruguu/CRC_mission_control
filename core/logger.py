import logging
import csv
import os
from datetime import datetime
from pathlib import Path
from core.data_types import TelemetryFrame


class DPGHandler(logging.Handler):
    """Specjalny handler przesyłający logi bezpośrednio do interfejsu Dear PyGui."""

    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def emit(self, record):
        log_entry = self.format(record)
        # Przekazanie sformatowanego tekstu do funkcji UI
        if self.callback:
            self.callback(log_entry, record.levelno)


class MissionLogger:
    def __init__(self, log_dir="logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)

        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.telemetry_file = self.log_dir / f"telemetry_{self.session_id}.csv"
        self.system_file = self.log_dir / f"system_{self.session_id}.log"

        self._setup_system_logger()
        self._setup_csv_header()

    def _setup_system_logger(self):
        """Konfiguracja standardowego loggera Pythona dla zdarzeń systemowych."""
        self.logger = logging.getLogger("MissionControl")
        self.logger.setLevel(logging.DEBUG)

        formatter = logging.Formatter(
            '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
            datefmt='%H:%M:%S'
        )

        # Logowanie do pliku tekstowego
        file_handler = logging.FileHandler(self.system_file)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        # Logowanie do konsoli (opcjonalnie)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def _setup_csv_header(self):
        """Inicjalizacja pliku CSV z nagłówkami telemetrycznymi."""
        headers = [
            "timestamp", "frame_id", "state",
            "acc_x", "acc_y", "acc_z",
            "gyr_x", "gyr_y", "gyr_z",
            "alt", "lat", "lon", "temp", "volt", "curr"
        ]
        with open(self.telemetry_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(headers)

    def log_telemetry(self, frame: TelemetryFrame):
        """Zapisuje pełną ramkę danych do pliku CSV."""
        try:
            with open(self.telemetry_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().timestamp(),
                    frame.frame_id,
                    frame.state.value,
                    frame.accel.x, frame.accel.y, frame.accel.z,
                    frame.gyro.x, frame.gyro.y, frame.gyro.z,
                    frame.altitude,
                    frame.latitude,
                    frame.longitude,
                    frame.temp_payload,
                    frame.voltage,
                    frame.current
                ])
        except Exception as e:
            self.error(f"Failed to write telemetry to CSV: {e}")

    # Metody pomocnicze dla logowania systemowego
    def info(self, msg):
        self.logger.info(msg)

    def debug(self, msg):
        self.logger.debug(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def add_ui_handler(self, callback):
        """Podpięcie terminala DPG do strumienia logów."""
        handler = DPGHandler(callback)
        formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s', '%H:%M:%S')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)