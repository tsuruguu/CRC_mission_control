import dearpygui.dearpygui as dpg
from core.data_types import ConnectionStatus, MissionState
import ui.theme as theme


class StatusIndicator:
    """Komponent obsługujący 5-kolorową diodę statusu oraz wskaźniki aktywności RX/TX."""

    @staticmethod
    def set_main_led(status: ConnectionStatus):
        """Ustawia kolor głównego LED-a zgodnie z logiką połączenia[cite: 2, 11]."""
        # status.value zawiera krotkę (R, G, B) zdefiniowaną w data_types.py[cite: 5]
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
    """Zaawansowana obsługa logów systemowych i telemetrii[cite: 11]."""

    def __init__(self, item_tag):
        self.tag = item_tag
        self.buffer = []
        self.max_lines = 1000  # Zwiększony limit dla lepszej diagnostyki[cite: 11]

    def append(self, text: str, level: str = "INFO"):
        """Dodaje sformatowaną linię do terminala z obsługą poziomów logowania[cite: 4, 11]."""
        timestamp = dpg.get_value("bitrate_text")  # Opcjonalnie można użyć czasu systemowego
        new_line = f"[{level}] {text}"
        self.buffer.append(new_line)

        # Utrzymywanie wydajności poprzez limitowanie bufora[cite: 11]
        if len(self.buffer) > self.max_lines:
            self.buffer.pop(0)

        # Aktualizacja widżetu w DPG
        dpg.set_value(self.tag, "\n".join(self.buffer))

        # Obsługa automatycznego przewijania (Autoscroll)[cite: 11, 14]
        if dpg.get_value("autoscroll_check"):
            dpg.set_y_scroll(self.tag, -1.0)

    def clear(self):
        """Czyści całą zawartość okna terminala[cite: 15]."""
        import logging
        logging.getLogger("MissionControl").info("User cleared terminal buffer")  # <--- LOG CLEAR[cite: 21]
        self.buffer = []
        dpg.set_value(self.tag, "")


class FlightDataDisplays:
    """Zarządzanie dynamicznymi wskaźnikami tekstowymi telemetrii[cite: 1, 11]."""

    @staticmethod
    def update_metrics(alt: float, volt: float, temp: float, strain: float):
        """Aktualizuje liczbowe dane telemetryczne i monitoruje bezpieczeństwo[cite: 1, 11]."""
        import logging
        logger = logging.getLogger("MissionControl")

        dpg.set_value("alt_display", f"ALTITUDE: {alt:.1f} m")
        dpg.set_value("temp_display", f"PAYLOAD TEMP: {temp:.1f} °C")

        dpg.set_value("volt_display", f"VOLTAGE: {volt:.2f} V")
        if volt < 3.4:
            dpg.configure_item("volt_display", color=theme.STATUS_RED)
            # Loguj rzadziej (np. tylko przy pierwszym spadku) lub na poziomie DEBUG
        else:
            dpg.configure_item("volt_display", color=theme.TEXT_MAIN)

        if strain > 100.0:
            dpg.configure_item("status_msg_text", color=theme.STATUS_AMBER)
            dpg.set_value("status_msg_text", "HIGH STRAIN DETECTED")
            # DODAJ TO: Zapis do pliku logów[cite: 21]
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