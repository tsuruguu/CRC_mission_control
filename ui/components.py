import dearpygui.dearpygui as dpg
from core.data_types import ConnectionStatus, MissionState
import ui.theme as theme
from collections import deque
import numpy as np
import time
import logging

logger = logging.getLogger("MissionControl")

class StatusIndicator:
    """Komponent obsługujący 5-kolorową diodę statusu oraz wskaźniki aktywności RX/TX."""

    @staticmethod
    def set_led(tag, color):
        """Uniwersalna metoda do ustawiania koloru dowolnego LED-a[cite: 40]."""
        dpg.configure_item(tag, fill=color)

    @staticmethod
    def set_main_led(status: ConnectionStatus):
        """Ustawia kolor głównego LED-a zgodnie ze stanem połączenia[cite: 40]."""
        dpg.configure_item("main_status_led", fill=status.value)

    @staticmethod
    def blink_tx():
        """Sygnalizuje wysłanie komendy do rakiety błyskiem diody TX[cite: 11]."""
        dpg.configure_item("tx_led", fill=theme.STATUS_BLUE)
        # Reset koloru nastąpi automatycznie przy braku aktywności w pętli main

    @staticmethod
    def blink_rx():
        """Sygnalizuje odebranie poprawnej ramki LoRa błyskiem diody RX[cite: 11]."""
        dpg.configure_item("rx_led", fill=theme.STATUS_GREEN)


class TerminalComponent:
    """Zaawansowana obsługa logów systemowych i telemetrii."""

    def __init__(self, item_tag, parent_tag, scroll_check_tag="autoscroll_check"): # DODAJ parent_tag tutaj
        self.tag = item_tag
        self.parent_tag = parent_tag
        self.scroll_check_tag = scroll_check_tag  # Dynamiczny tag checkboxa
        self.buffer = []
        self.max_lines = 300
        self._needs_update = False
        self._last_scroll_state = True

    def append(self, text: str, level=None):
        self.buffer.append(text)
        if len(self.buffer) > self.max_lines:
            self.buffer.pop(0)
        self._needs_update = True

    def update_ui(self):
        """Wywoływane raz na klatkę w pętli głównej."""
        current_scroll_state = dpg.get_value(self.scroll_check_tag)

        # Wykrywamy moment włączenia checkboxa (Toggle ON)
        toggled_on = current_scroll_state and not self._last_scroll_state
        self._last_scroll_state = current_scroll_state

        # 1. Jeśli doszły nowe dane - aktualizujemy tekst
        if self._needs_update:
            dpg.set_value(self.tag, "\n".join(self.buffer))
            self._needs_update = False

            # Jeśli autoscroll jest ON, przewijamy przy nowych danych
            if current_scroll_state:
                self._do_scroll()

        # 2. Jeśli użytkownik właśnie zaznaczył AUTO (nawet bez nowych danych) - skocz na dół
        elif toggled_on:
            self._do_scroll()

    def _do_scroll(self):
        """Wewnętrzna metoda do przewijania na sam dół."""
        try:
            # Używamy bardzo dużej wartości, by mieć pewność, że dotrzemy do końca
            dpg.set_y_scroll(self.parent_tag, 1000000)
        except:
            pass

    def clear(self):
        self.buffer = []
        dpg.set_value(self.tag, "")
        dpg.set_y_scroll(self.parent_tag, 0.0)
        self._needs_update = False


class FlightDataDisplays:
    """Zarządzanie dynamicznymi wskaźnikami tekstowymi telemetrii[cite: 1, 11]."""

    @staticmethod
    def update_metrics(alt: float, volt: float, temp: float, strain: float):
        """Aktualizuje liczbowe dane telemetryczne i monitoruje bezpieczeństwo[cite: 1, 11]."""
        dpg.set_value("alt_display", f"ALTITUDE: {alt:.1f} m")
        dpg.set_value("temp_display", f"PAYLOAD TEMP: {temp:.1f} °C")
        dpg.set_value("volt_display", f"VOLTAGE: {volt:.2f} V")

        # Alert napięcia baterii 18650[cite: 1, 4]
        if volt < 3.4:
            dpg.configure_item("volt_display", color=theme.STATUS_RED)
        else:
            dpg.configure_item("volt_display", color=theme.TEXT_MAIN)

        if strain > 100.0:
            dpg.configure_item("status_msg_text", color=theme.STATUS_AMBER)
            dpg.set_value("status_msg_text", "HIGH STRAIN DETECTED")
            logger.warning(f"KRYTYCZNE NAPRĘŻENIA KONSTRUKCJI: {strain:.2f}")

    @staticmethod
    def update_metrics(alt: float, volt: float, temp: float, strain: float):
        """Aktualizuje liczbowe dane telemetryczne i monitoruje bezpieczeństwo[cite: 1, 11]."""
        dpg.set_value("alt_display", f"ALTITUDE: {alt:.1f} m")
        dpg.set_value("temp_display", f"PAYLOAD TEMP: {temp:.1f} °C")

        # Monitorowanie napięcia 18650 (Alert poniżej 3.4V)[cite: 1, 11]
        dpg.set_value("volt_display", f"VOLTAGE: {volt:.2f} V")
        if volt < 3.4:
            dpg.configure_item("volt_display", color=theme.STATUS_RED)
        else:
            dpg.configure_item("volt_display", color=theme.TEXT_MAIN)

        # Opcjonalnie: logowanie ostrzeżeń o naprężeniach (strain_gauge)
        if strain > 100.0:  # Przykładowy próg wytrzymałości konstrukcji
            dpg.configure_item("status_msg_text", color=theme.STATUS_AMBER)
            dpg.set_value("status_msg_text", "HIGH STRAIN DETECTED")

    @staticmethod
    def update_state(state_enum):
        """Aktualizuje tekstowy opis stanu misji[cite: 9]."""
        try:
            dpg.set_value("state_display", f"STATE: {state_enum.value}")
        except:
            pass


class PayloadManager:
    """Zarządza danymi wykresu i dużymi wyświetlaczami Payloadu[cite: 1, 13]."""

    def __init__(self, plot_tag, max_points=200):
        self.plot_tag = plot_tag
        self.max_points = max_points
        self.times = deque(maxlen=max_points)
        self.temps = deque(maxlen=max_points)
        self.start_time = time.time()

    def update(self, temp_val, uv_val=0):
        """Aktualizuje dane na wykresie i wskaźnikach tekstowych[cite: 13, 23]."""
        elapsed = time.time() - self.start_time
        self.times.append(elapsed)
        self.temps.append(temp_val)

        # NumPy optymalizuje przesyłanie danych do GPU[cite: 13, 28]
        dpg.set_value(self.plot_tag, [list(self.times), list(self.temps)])

        # Aktualizacja dużych napisów z Unknown-4_2.jpg[cite: 14]
        dpg.set_value("big_temp_val", f"{temp_val:.1f} °C")
        dpg.set_value("big_uv_val", f"{int(uv_val)}")

        # Przesunięcie osi czasu
        if len(self.times) > 1:
            dpg.set_axis_limits("temp_x_axis", self.times[0], self.times[-1])