import serial
import time
import math
import random


class RocketSimulator:
    def __init__(self, port='/tmp/virtualCOM1', baudrate=115200):
        try:
            self.ser = serial.Serial(port, baudrate, timeout=1)
            print(f"🚀 Simulator started on {port}")
        except Exception as e:
            print(f"❌ Error: Could not open port {port}. {e}")
            exit()

        # Stan fizyczny rakiety
        self.frame_id = 0
        self.state = "IDLE"
        self.start_time = time.time()
        self.altitude = 0.0
        self.velocity = 0.0
        self.pitch = 0.0
        self.roll = 0.0
        self.yaw = 0.0
        self.voltage = 4.2  # Start od w pełni naładowanej baterii 18650[cite: 1]

    def update_physics(self):
        """Generuje fizykę misji zgodną z raportem CRC 2026[cite: 1]."""
        elapsed = time.time() - self.start_time

        # Prosta maszyna stanów[cite: 22, 34]
        if self.state == "IDLE" and elapsed > 5:
            self.state = "LAUNCH"
        elif self.state == "LAUNCH" and elapsed > 6:
            self.state = "ASCENT"
        elif self.state == "ASCENT" and self.velocity < 0:
            self.state = "APOGEE"
        elif self.state == "APOGEE":
            self.state = "DESCENT"
        elif self.state == "DESCENT" and self.altitude <= 0:
            self.state = "LANDING"
            self.altitude = 0

        # Modelowanie lotu
        if self.state == "LAUNCH":
            self.velocity += 8.8  # G-force[cite: 1]
            self.altitude += self.velocity * 0.1
        elif self.state == "ASCENT":
            self.velocity -= 0.98  # Grawitacja
            self.altitude += self.velocity * 0.1
            self.pitch = 85.0 + random.uniform(-2, 2)
            self.roll += 5.0  # Obrót stabilizacyjny[cite: 1]
        elif self.state == "DESCENT":
            self.velocity = -8.0  # Docelowa prędkość opadania[cite: 1]
            self.altitude += self.velocity * 0.1
            self.pitch = random.uniform(-10, 10)
            self.roll += 2.0

        # Degradacja baterii i szum tensometrów[cite: 1, 34]
        self.voltage -= 0.0001  # Powolne rozładowywanie
        strain = abs(self.velocity * 0.5) + random.uniform(0, 5)

        return strain

    def generate_frame(self):
        """Tworzy ramkę CSV zgodną z TelemetryParser."""
        strain = self.update_physics()
        self.frame_id += 1

        # Konstrukcja ramki: ID;STATE;ACC_X;ACC_Y;ACC_Z;GYR_X;GYR_Y;GYR_Z;MAG_X;MAG_Y;MAG_Z;ALT;LAT;LON;TEMP;VOLT;CURR;STRAIN;P;R;Y
        frame = [
            str(self.frame_id),
            self.state,
            "0.1", "0.2", str(round(9.8 + (self.velocity * 0.1), 2)),  # ACC
            "0.01", "0.01", "0.01",  # GYR
            "120", "45", "10",  # MAG
            str(round(self.altitude, 2)),
            "50.06", "19.94",  # GPS (Kraków AGH)[cite: 1]
            str(round(20.0 + math.sin(time.time()) * 2, 2)),  # TEMP (Bio)[cite: 1]
            str(round(self.voltage, 2)),
            "0.5",  # CURR
            str(round(strain, 2)),
            str(round(self.pitch, 2)),
            str(round(self.roll % 360, 2)),
            str(round(self.yaw, 2))
        ]
        return ";".join(frame)

    def run(self):
        """Wysyła dane z częstotliwością 20Hz (co 50ms)."""
        while True:
            try:
                line = self.generate_frame()
                self.ser.write(f"{line}\n".encode())
                # Co 50 ramek symuluj "LUKĘ" w transmisji (test statusu YELLOW)[cite: 25]
                if self.frame_id % 50 == 0:
                    self.frame_id += 2

                time.sleep(0.05)
            except KeyboardInterrupt:
                self.ser.close()
                print("\n🛑 Simulator stopped.")
                break


if __name__ == "__main__":
    # Upewnij się, że port zgadza się z Twoim mostkiem!
    sim = RocketSimulator(port='/tmp/virtualCOM1')
    sim.run()