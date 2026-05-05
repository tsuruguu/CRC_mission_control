import dearpygui.dearpygui as dpg
from core.data_types import ConnectionStatus, MissionState
import ui.theme as theme


class StatusIndicator:
    """Komponent obsługujący 5-kolorową diodę statusu oraz diody TX/RX."""

    @staticmethod
    def set_main_led(status: ConnectionStatus):
        """Ustawia kolor głównego LED-a zgodnie ze specyfikacją."""
        # status.value zwraca krotkę (R, G, B) z data_types.py
        dpg.configure_item("main_status_led", fill=status.value)

    @staticmethod
    def blink_tx():
        """Krótki błysk diody TX przy wysyłaniu danych."""
        dpg.configure_item("tx_led", fill=theme.STATUS_BLUE)
        # W DPG najlepiej użyć timera lub po prostu resetować kolor w następnej klatce

    @staticmethod
    def blink_rx():
        """Błysk diody RX przy poprawnym odebraniu ramki."""
        dpg.configure_item("rx_led", fill=theme.STATUS_GREEN)


class TerminalComponent:
    """Obsługa logów i telemetrii w oknie terminala."""

    def __init__(self, item_tag):
        self.tag = item_tag
        self.buffer = []
        self.max_lines = 500  # Limit bufora dla wydajności

    def append(self, text, level="INFO"):
        """Dodaje nową linię do terminala z automatycznym przewijaniem."""
        self.buffer.append(f"[{level}] {text}")

        # Utrzymywanie limitu linii
        if len(self.buffer) > self.max_lines:
            self.buffer.pop(0)

        new_content = "\n".join(self.buffer)
        dpg.set_value(self.tag, new_content)

        # Logika AUTOSCROLL z Twojego rysunku
        if dpg.get_value("autoscroll_check"):
            dpg.set_y_scroll(self.tag, -1.0)  # Przewiń na sam dół

    def clear(self):
        """Czyści bufor i okno terminala."""
        self.buffer = []
        dpg.set_value(self.tag, "")


class FlightDataDisplays:
    """Uaktualnianie tekstowych wskaźników telemetrii[cite: 1]."""

    @staticmethod
    def update_state(state: MissionState):
        """Aktualizuje wyświetlany stan FSM rakiety[cite: 1]."""
        color = theme.TEXT_MAIN
        if state == MissionState.ASCENT: color = theme.STATUS_BLUE
        if state == MissionState.APOGEE: color = theme.STATUS_AMBER
        if state == MissionState.LANDING: color = theme.STATUS_GREEN

        dpg.set_value("state_display", f"STATE: {state.value}")
        dpg.configure_item("state_display", color=color)

    @staticmethod
    def update_metrics(alt, volt, curr):
        """Aktualizuje liczbowe dane lotu i zasilania 18650[cite: 1]."""
        dpg.set_value("alt_display", f"ALTITUDE: {alt:.1f} m")
        dpg.set_value("volt_display", f"VOLTAGE: {volt:.2f} V")

        # Alert niskiego napięcia baterii[cite: 1]
        if volt < 3.4:
            dpg.configure_item("volt_display", color=theme.STATUS_RED)
        else:
            dpg.configure_item("volt_display", color=theme.TEXT_MAIN)