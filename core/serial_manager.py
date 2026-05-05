import serial
import serial.tools.list_ports
import threading
import queue
import time

class SerialManager:
    def __init__(self):
        self.ser = None
        self.is_running = False
        self.read_thread = None
        self.raw_queue = queue.Queue()  # Telemetria do GUI
        self.status = "DISCONNECTED"    # BLACK, GREEN, RED, YELLOW, BLUE

    def scan_ports(self):
        """Zwraca listę dostępnych portów COM."""
        return [port.device for port in serial.tools.list_ports.comports()]

    def connect(self, port, baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=0.1)
            self.is_running = True
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()
            self.status = "CONNECTED"
            return True
        except Exception as e:
            print(f"Błąd połączenia: {e}")
            self.status = "ERROR"
            return False

    def disconnect(self):
        self.is_running = False
        if self.ser:
            self.ser.close()
        self.status = "DISCONNECTED"

    def _read_loop(self):
        """Wątek pracujący w tle, nie muli GUI."""
        while self.is_running:
            if self.ser and self.ser.in_waiting > 0:
                try:
                    line = self.ser.readline().decode('utf-8').strip()
                    if line:
                        self.raw_queue.put(line)
                except Exception:
                    self.status = "ERROR"
            time.sleep(0.01) # Oszczędność CPU

    def send_data(self, data):
        """Wysyła tekst do rakiety (np. komendy armingu)."""
        if self.ser and self.ser.is_open:
            self.ser.write(f"{data}\n".encode())
            return True
        return False