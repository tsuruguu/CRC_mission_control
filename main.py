import dearpygui.dearpygui as dpg
import time
from core.serial_manager import SerialManager
from core.telemetry import TelemetryParser
from core.logger import MissionLogger
from core.data_types import ConnectionStatus
from ui.layout import MissionControlLayout
from ui.components import StatusIndicator, TerminalComponent, FlightDataDisplays
import ui.theme as theme


class MissionControlApp:
    def __init__(self):
        # Inicjalizacja Core[cite: 3, 4]
        self.serial = SerialManager()
        self.parser = TelemetryParser()
        self.logger = MissionLogger()

        # Inicjalizacja UI[cite: 11, 14]
        self.layout = MissionControlLayout()
        self.terminal = None

        # Setup DPG[cite: 12]
        dpg.create_context()
        theme.apply_skylink_theme()
        theme.setup_fonts()

    def setup(self):
        """Konfiguracja okna i callbacków[cite: 18]."""
        self.logger.info("Initializing UI Layout...")  # <--- LOG STARTU UI[cite: 21]
        dpg.create_viewport(title='FST AGH - Mission Control v2', width=1300, height=800)
        self.layout.create_layout()

        # Inicjalizacja terminala i podpięcie loggera[cite: 4, 11]
        self.terminal = TerminalComponent(self.layout.terminal_id)
        self.logger.add_ui_handler(self.terminal.append)

        # Podpięcie callbacków do przycisków[cite: 14]
        dpg.configure_item("scan_btn", callback=self._on_scan)
        dpg.configure_item("connect_btn", callback=self._on_connect)
        dpg.configure_item("send_btn", callback=self._on_send)
        dpg.configure_item("clear_btn", callback=lambda: self.terminal.clear())

        # Przyciski krytyczne[cite: 1]
        dpg.configure_item("arm_btn", callback=lambda: self._send_cmd("ARM"))
        dpg.configure_item("abort_btn", callback=lambda: self._send_cmd("ABORT"))

        dpg.configure_item("drogue_btn", callback=lambda: self._send_cmd("DEPLOY_DROGUE"))
        dpg.configure_item("main_para_btn", callback=lambda: self._send_cmd("DEPLOY_MAIN"))
        dpg.configure_item("reset_btn", callback=lambda: self._send_cmd("RESET_DYNAMIXELS"))

    def _on_scan(self):
        """Skanowanie dostępnych portów COM."""
        ports = self.serial.scan_ports()
        dpg.configure_item("port_combo", items=ports)
        self.logger.info(f"Scanned ports: {ports}")

    def _on_connect(self):
        """Obsługa łączenia/rozłączania[cite: 3]."""
        if self.serial.is_running:
            self.serial.disconnect()
            self.logger.warning("Disconnected from port")
        else:
            port = dpg.get_value("port_combo")
            if port and self.serial.connect(port):
                self.logger.info(f"Connected to {port}")
            else:
                self.logger.error("Failed to connect!")

    def _on_send(self):
        """Wysyłanie ręcznej komendy[cite: 11]."""
        cmd = dpg.get_value("cmd_input")
        if self._send_cmd(cmd):
            dpg.set_value("cmd_input", "")

    def _send_cmd(self, cmd):
        """Logika wysyłania danych do rakiety[cite: 3, 11]."""
        if self.serial.send_data(cmd):
            StatusIndicator.blink_tx()
            self.logger.info(f"Sent command: {cmd}")
            return True
        return False

    def run(self):
        """Główna pętla aplikacji (Real-time update)[cite: 13, 14]."""
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)

        self.logger.info("Mission Control Started")

        while dpg.is_dearpygui_running():
            # 1. Przetwarzanie kolejki telemetrii[cite: 2, 3]
            while not self.serial.raw_queue.empty():
                raw_line = self.serial.raw_queue.get()
                frame = self.parser.parse_line(raw_line)

                if frame:
                    # Logowanie i błysk RX[cite: 4, 11]
                    self.logger.log_telemetry(frame)
                    StatusIndicator.blink_rx()

                    # Aktualizacja Navballa[cite: 13]
                    self.layout.navball.update(frame.pitch, frame.roll, frame.yaw)

                    # Aktualizacja wyświetlaczy[cite: 11]
                    FlightDataDisplays.update_state(frame.state)
                    FlightDataDisplays.update_metrics(
                        frame.altitude, frame.voltage, frame.temp, frame.strain_gauge
                    )

            # 2. Aktualizacja statusów systemowych[cite: 11, 14]
            current_status = self.parser.get_connection_status()
            StatusIndicator.set_main_led(current_status)
            dpg.set_value("bitrate_text", f"{self.serial.bitrate:.1f} kb/s")

            # 3. Renderowanie klatki
            dpg.render_dearpygui_frame()

        # Shutdown
        self.logger.info("Mission Control Session Ended")  # <--- DODAJ TO[cite: 21]
        self.serial.disconnect()
        dpg.destroy_context()


if __name__ == "__main__":
    app = MissionControlApp()
    app.setup()
    app.run()