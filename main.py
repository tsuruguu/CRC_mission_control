import dearpygui.dearpygui as dpg
import time
from core.serial_manager import SerialManager
from core.telemetry import TelemetryParser
from core.logger import MissionLogger
from core.data_types import ConnectionStatus
from ui.layout import MissionControlLayout
from ui.components import StatusIndicator, TerminalComponent, FlightDataDisplays
import ui.theme as theme
from ui.components import PayloadManager


class MissionControlApp:
    def __init__(self):
        # Inicjalizacja Core[cite: 3, 4]
        self.serial = SerialManager()
        self.parser = TelemetryParser()
        self.logger = MissionLogger()

        # Inicjalizacja UI[cite: 11, 14]
        self.layout = MissionControlLayout()
        self.terminal = None
        self.payload_mgr = None

        self.raw_feed_buffer = []

        self.terminal_raw = TerminalComponent("raw_telemetry_feed", "raw_feed_container")

        # Setup DPG[cite: 12]
        dpg.create_context()
        theme.apply_skylink_theme()
        theme.setup_fonts()

    def setup(self):
        """Konfiguracja okna i callbacków[cite: 18]."""
        self.logger.info("Initializing UI Layout...")  # <--- LOG STARTU UI[cite: 21]
        dpg.create_viewport(title='FST AGH - Mission Control v2', width=1300, height=800)
        dpg.set_viewport_min_width(1200)
        dpg.set_viewport_min_height(700)
        self.layout.create_layout()
        self.payload_mgr = PayloadManager("temp_plot_series")

        # 1. Terminal główny (Logger) - korzysta z dolnego checkboxa
        self.terminal = TerminalComponent(
            self.layout.terminal_id,
            "terminal_container",
            "autoscroll_check"
        )

        # 2. Terminal RAW - korzysta z checkboxa w zakładce Communication
        self.terminal_raw = TerminalComponent(
            "raw_telemetry_feed",
            "raw_feed_container",
            "raw_autoscroll_check"
        )

        # 3. Terminal CMD - korzysta z drugiego checkboxa w zakładce
        self.terminal_cmd = TerminalComponent(
            "command_console",
            "command_console_container",
            "cmd_autoscroll_check"
        )

        self.logger.add_ui_handler(self.terminal.append)

        # Podpięcie callbacków do przycisków[cite: 14]
        dpg.configure_item("scan_btn", callback=self._on_scan)
        dpg.configure_item("connect_btn", callback=self._on_connect)
        dpg.configure_item("send_btn", callback=self._on_send)
        dpg.configure_item("cmd_input", callback=self._on_send, on_enter=True)

        dpg.configure_item("clear_raw_btn", callback=self.terminal_raw.clear)
        dpg.configure_item("clear_cmd_btn", callback=self.terminal_cmd.clear)

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

    # main.py - Poprawione metody klasy MissionControlApp

    def _on_send(self):
        """Wysyła komendę, czyści pole i przywraca fokus kursora."""
        cmd = dpg.get_value("cmd_input")
        if not cmd.strip():
            return

        # Wywołanie metody wysyłania
        if self._send_cmd(cmd):
            dpg.set_value("cmd_input", "")
        else:
            self.logger.error(f"Nie udało się wysłać: {cmd} (Brak połączenia?)")

        # Przywrócenie fokusu, by móc pisać dalej bez klikania myszką
        dpg.focus_item("cmd_input")

    def _send_cmd(self, cmd):
        """Logika wysyłania danych przez port szeregowy[cite: 26]."""
        if self.serial.send_data(cmd):
            StatusIndicator.blink_tx()
            self.logger.info(f"Sent: {cmd}")
            self._log_command(f"TX > {cmd}")
            return True
        return False

    def _log_raw(self, text):
        """Logowanie surowych danych i przewijanie kontenera[cite: 14]."""
        current_val = dpg.get_value("raw_telemetry_feed")
        lines = (current_val + "\n" + text).split('\n')
        dpg.set_value("raw_telemetry_feed", "\n".join(lines[-50:]))

        if dpg.get_value("raw_autoscroll_check"):
            try:
                # Przewijamy kontener okna, nie pole tekstowe[cite: 14]
                dpg.set_y_scroll("raw_feed_container", -1.0)
            except:
                pass

    def _append_to_feed(self, text):
        """Dodaje nową linię do panelu TELEMETRY FEED w zakładce COMMUNICATION."""
        self.raw_feed_buffer.append(text)

        # Trzymamy tylko 100 ostatnich linii, żeby nie obciążać aplikacji
        if len(self.raw_feed_buffer) > 100:
            self.raw_feed_buffer.pop(0)

        try:
            # Wpisz tekst do pola
            dpg.set_value("raw_telemetry_feed", "\n".join(self.raw_feed_buffer))

            # Autoscroll (przewijanie na sam dół)
            if dpg.get_value("autoscroll_check"):
                dpg.set_y_scroll("raw_telemetry_container", -1.0)
        except Exception:
            pass

    def run(self):
        """Główna pętla aplikacji (Real-time update)[cite: 13, 14]."""
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Primary Window", True)

        self.logger.info("Mission Control Started")

        while dpg.is_dearpygui_running():
            while not self.serial.raw_queue.empty():
                raw_line = self.serial.raw_queue.get()

                # 1. Zapis do pliku (logowanie osobne)
                self.logger.log_raw_frame(raw_line)

                # 2. Wyświetlanie w UI z poprawionym scrollem
                self.terminal_raw.append(f"RX > {raw_line}")

                # 3. Parsowanie (Twoja dotychczasowa logika)
                frame = self.parser.parse_line(raw_line)
                if frame:
                    self.layout.navball.update(frame.pitch, frame.roll, frame.yaw)
                    self.logger.log_telemetry(frame)
                    StatusIndicator.blink_rx()

                    # Aktualizacja Navballa[cite: 13]
                    self.layout.navball.update(frame.pitch, frame.roll, frame.yaw)

                    # Aktualizacja wyświetlaczy[cite: 11]
                    FlightDataDisplays.update_state(frame.state)
                    FlightDataDisplays.update_metrics(
                        frame.altitude, frame.voltage, frame.temp, frame.strain_gauge
                    )
                    if self.payload_mgr:
                        self.payload_mgr.update(frame.temp_payload, frame.current)

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

    def _log_raw(self, text):
        """Loguje surową telemetrię i przewija RAW FEED."""
        current_val = dpg.get_value("raw_telemetry_feed")
        lines = (current_val + "\n" + text).split('\n')
        dpg.set_value("raw_telemetry_feed", "\n".join(lines[-50:]))

        if dpg.get_value("raw_autoscroll_check"):
            try:
                # Przewijanie do aktualnego maksimum kontenera
                dpg.set_y_scroll("raw_feed_container", dpg.get_y_scroll_max("raw_feed_container"))
            except:
                pass

    def _log_command(self, text):
        """Loguje komendy i przewija COMMAND CONSOLE."""
        current_val = dpg.get_value("command_console")
        dpg.set_value("command_console", current_val + "\n" + text)

        if dpg.get_value("cmd_autoscroll_check"):
            try:
                # Przewijanie do aktualnego maksimum kontenera
                dpg.set_y_scroll("command_console_container", dpg.get_y_scroll_max("command_console_container"))
            except:
                pass


if __name__ == "__main__":
    app = MissionControlApp()
    app.setup()
    app.run()