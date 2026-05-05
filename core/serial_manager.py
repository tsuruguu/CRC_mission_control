import serial
import serial.tools.list_ports
import threading
import queue
import time
import logging
import glob
import sys

from core.data_types import ConnectionStatus


class SerialManager:
    def __init__(self):
        self.ser = None
        self.is_running = False
        self.read_thread = None
        self.raw_queue = queue.Queue()  # Kolejka surowych linii dla parsera
        self.status = ConnectionStatus.DISCONNECTED
        self.logger = logging.getLogger("MissionControl")

        # Statystyki wydajności dla UI
        self.bitrate = 0.0
        self._bytes_count = 0
        self._last_stat_time = time.time()

    def scan_ports(self):
        """Zwraca listę portów, uwzględniając wirtualne porty na macOS."""
        # Standardowe skanowanie sprzętowe
        ports = [port.device for port in serial.tools.list_ports.comports()]

        # Dodatek dla macOS: szukanie portów stworzonych przez socat
        if sys.platform.startswith('darwin'):
            # Szukamy wzorca /dev/ttys* (standard dla PTY na Macu)
            # Możesz też dodać /dev/cu.* jeśli socat takowe stworzy
            virtual_ptys = glob.glob('/dev/ttys[0-9][0-9][0-9]')
            for p in virtual_ptys:
                if p not in ports:
                    ports.append(p)

        self.logger.info(f"Scanned ports: {ports}")
        return ports

    def connect(self, port, baudrate=115200):
        """Inicjalizuje połączenie z STM32/LoRa."""
        self.logger.info(f"Attempting to connect to {port} at {baudrate} baud...")  # <--- LOG INFO
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            self.is_running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            self.status = ConnectionStatus.CONNECTED
            self.logger.info(f"Successfully connected to {port}")  # <--- LOG INFO[cite: 3, 4, 24]
            return True
        except Exception as e:
            self.logger.error(f"Failed to connect to {port}: {e}")  # <--- LOG ERROR[cite: 4, 24]
            self.status = ConnectionStatus.ERROR
            return False

    def disconnect(self):
        """Zatrzymuje wątek i bezpiecznie zamyka port."""
        if not self.is_running:
            return

        self.is_running = False
        if self.read_thread:
            self.read_thread.join(timeout=1.0)
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.logger.warning("Serial connection closed by user")  # <--- LOG WARNING[cite: 4, 24]
        self.status = ConnectionStatus.DISCONNECTED

    def _read_loop(self):
        """Wątek w tle odciążający GUI od operacji I/O[cite: 3]."""
        while self.is_running:
            if self.ser and self.ser.is_open:
                try:
                    if self.ser.in_waiting > 0:
                        line = self.ser.readline()
                        self._bytes_count += len(line)

                        # Próba dekodowania (ignorowanie błędnych bajtów LoRa)
                        decoded_line = line.decode('utf-8', errors='ignore').strip()
                        if decoded_line:
                            self.raw_queue.put(decoded_line)

                    # Obliczanie bitrate co 1 sekundę
                    self._update_bitrate()

                except Exception:
                    self.logger.critical(f"Serial read error: {e}")
                    self.status = ConnectionStatus.ERROR
                    self.is_running = False
            time.sleep(0.001)  # Minimalne opóźnienie dla zachowania responsywności CPU

    def _update_bitrate(self):
        """Oblicza aktualną prędkość transmisji w kb/s."""
        now = time.time()
        diff = now - self._last_stat_time
        if diff >= 1.0:
            self.bitrate = (self._bytes_count * 8) / (diff * 1024)  # kb/s
            self._bytes_count = 0
            self._last_stat_time = now

    def send_data(self, data):
        """Wysyła komendy do rakiety."""
        if self.ser and self.ser.is_open:
            try:
                self.ser.write(f"{data}\n".encode())
                self.logger.debug(f"Raw data sent: {data}")  # <--- LOG DEBUG[cite: 4, 24]
                return True
            except Exception as e:
                self.logger.error(f"Failed to send data '{data}': {e}")  # <--- LOG ERROR[cite: 4, 24]
                self.status = ConnectionStatus.ERROR
        return False