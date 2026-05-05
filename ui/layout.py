import dearpygui.dearpygui as dpg
from ui.navball import NavballWidget
import ui.theme as theme


class MissionControlLayout:
    def __init__(self):
        self.navball = None
        self.terminal_id = "telemetry_feed_terminal"

    def create_layout(self):
        # Główny kontener zajmujący całe dostępne okno (Viewport)
        with dpg.window(tag="Primary Window", no_title_bar=True, no_move=True, no_resize=True):
            # --- 1. TOP BAR (COMMUNICATION & STATUS) ---
            # Zawiera wskaźnik bitrate, wybór portu i diody statusu[cite: 1, 14]
            with dpg.child_window(height=60, border=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("0.0 kb/s", tag="bitrate_text", color=theme.SKYLINK_TEAL)
                    dpg.add_spacer(width=20)

                    dpg.add_button(label="SCAN", width=80, tag="scan_btn")
                    dpg.add_combo(items=[], label="", width=150, tag="port_combo")

                    # Główny status LED (Dioda 5-kolorowa)[cite: 11, 14]
                    with dpg.drawlist(width=30, height=30):
                        dpg.draw_circle((15, 15), 10, color=theme.SKYLINK_TEAL_TRANSPARENT, fill=(0, 0, 0),
                                        tag="main_status_led")

                    dpg.add_button(label="OPEN | CLOSE", width=120, tag="connect_btn")
                    dpg.add_button(label="STG", width=40, tag="settings_btn")

                    dpg.add_spacer(width=20)
                    # Wskaźniki aktywności radiowej TX / RX[cite: 11, 14]
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            dpg.add_text("TX", color=theme.TEXT_DIM, tag="tx_text")
                            with dpg.drawlist(width=15, height=15):
                                dpg.draw_circle((7, 7), 5, fill=(0, 0, 0), tag="tx_led")
                        with dpg.group(horizontal=True):
                            dpg.add_text("RX", color=theme.TEXT_DIM, tag="rx_text")
                            with dpg.drawlist(width=15, height=15):
                                dpg.draw_circle((7, 7), 5, fill=(0, 0, 0), tag="rx_led")

            dpg.add_separator()

            # --- 2. MAIN NAVIGATION TABS ---
            with dpg.tab_bar():
                # KARTA 1: HARDWARE (Przeniesiona dotychczasowa logika)[cite: 14]
                with dpg.tab(label="COMMUNICATION"):
                    with dpg.group(horizontal=True):
                        # Używamy ujemnej szerokości, aby terminal zabierał wszystko POZA miejscem na Navball
                        with dpg.child_window(width=-400, border=True, tag="raw_telemetry_container"):
                            dpg.add_text("TELEMETRY FEED", color=theme.SKYLINK_TEAL)
                            dpg.add_input_text(multiline=True, width=-1, height=-1, readonly=True,
                                               tag="raw_telemetry_feed")

                        # Navball ma stałą szerokość, co zapobiega jego deformacji na małych ekranach
                        with dpg.child_window(width=380, border=True):
                            nav_container = dpg.add_child_window(height=350, border=False)
                            self.navball = NavballWidget(nav_container)
                            dpg.add_separator()
                            # Dane pod Navballem
                            dpg.add_text("STATE: IDLE", tag="state_display")
                            dpg.add_text("ALTITUDE: 0.0 m", tag="alt_display")

                # KARTA 2: PAYLOAD (Zgodnie z Unknown-4_2.jpg)[cite: 1, 14]
                with dpg.tab(label="PAYLOAD"):
                    dpg.add_spacer(height=10)
                    dpg.add_text("ALGAE BIOLOGICAL PAYLOAD MONITOR", indent=550, color=theme.SKYLINK_TEAL)
                    dpg.add_spacer(height=20)

                    with dpg.group(horizontal=True):
                        # Sekcja temperatury
                        with dpg.child_window(width=400, height=150, border=False):
                            dpg.add_text("CURRENT TEMP", color=theme.TEXT_DIM)
                            dpg.add_text("20.0 °C", tag="big_temp_val",
                                         color=theme.STATUS_AMBER)  # Duży font ustawimy w theme
                            dpg.bind_item_font("big_temp_val", "big_payload_font")

                        # Sekcja UV
                        with dpg.child_window(width=400, height=150, border=False):
                            dpg.add_text("UV INTENSITY", color=theme.TEXT_DIM)
                            dpg.add_text("0", tag="big_uv_val", color=theme.STATUS_BLUE)
                            dpg.bind_item_font("big_uv_val", "big_payload_font")

                    # Wykres czasu rzeczywistego
                    dpg.add_text("Temperature variation (Real-time)", color=theme.TEXT_DIM)
                    with dpg.plot(height=-1, width=-1):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", tag="temp_x_axis")
                        y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Temp (°C)", tag="temp_y_axis")
                        dpg.add_line_series([], [], label="Temp Trend", parent=y_axis, tag="temp_plot_series")

                # KARTA 2: HARDWARE
                with dpg.tab(label="HARDWARE"):
                    # Dodajemy horizontal_scrollbar=True, aby na 768p można było przesunąć widok
                    with dpg.child_window(width=-1, height=-1, border=False, horizontal_scrollbar=True):
                        dpg.add_spacer(height=10)

                        # Pasek górny Hardware
                        with dpg.group(horizontal=True):
                            dpg.add_text("Crc 2026 Rocket Hardware", color=theme.SKYLINK_TEAL)
                            # Używamy spacji relatywnej zamiast stałej liczby pikseli
                            dpg.add_spacer(width=50)
                            dpg.add_button(label="Maintenance", width=120)
                            dpg.add_button(label="Snapshot", width=100)

                        dpg.add_spacer(height=10)

                        # Panele Hardware w grupie poziomej
                        with dpg.group(horizontal=True):
                            panel_w = 125
                            panel_h = 220

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("IMU_MPU9250", color=theme.TEXT_DIM)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("BARO_BMP280", color=theme.TEXT_DIM)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("GPS_GP02", color=theme.TEXT_DIM)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("BODY_STRESS", color=theme.TEXT_DIM)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("AERO_FINS", color=theme.TEXT_DIM)
                                dpg.add_spacer(height=20)
                                dpg.add_text("0", indent=55)
                                dpg.add_input_text(width=-1, default_value="--")
                                dpg.add_button(label="SET", width=-1)
                                dpg.add_spacer(height=10)
                                dpg.add_button(label="OPEN", width=-1)
                                dpg.add_button(label="CLOSE", width=-1)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("RECOVERY_SYS", color=theme.TEXT_DIM)
                                dpg.add_text("ARMED", color=theme.TEXT_DIM)
                                dpg.add_spacer(height=30)
                                dpg.add_button(label="ARM", width=-1)
                                dpg.add_button(label="DISARM", width=-1)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("BATTERY", color=theme.TEXT_DIM)
                                dpg.add_spacer(height=50)
                                dpg.add_button(label="OPEN", width=-1)
                                dpg.add_button(label="CLOSE", width=-1)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("SD_LOGGER", color=theme.TEXT_DIM)
                                dpg.add_spacer(height=25)
                                dpg.add_button(label="START", width=-1)
                                dpg.add_button(label="STOP", width=-1)
                                dpg.add_button(label="ERASE", width=-1)

                            with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                dpg.add_text("BUZZER_LEDS", color=theme.TEXT_DIM)
                                dpg.add_spacer(height=50)
                                dpg.add_button(label="OPEN", width=-1)
                                dpg.add_button(label="CLOSE", width=-1)

                            with dpg.child_window(width=panel_w + 15, height=panel_h, border=True):
                                dpg.add_text("FLIGHT_SCHED", color=theme.TEXT_DIM)
                                dpg.add_text("Seq State Unk", color=theme.TEXT_DIM, wrap=120)
                                dpg.add_spacer(height=10)
                                with dpg.group(horizontal=True):
                                    dpg.add_button(label="START", width=60)
                                    dpg.add_button(label="CLEAR", width=60)



                # KARTA 3: SEQUENCES
                with dpg.tab(label="SEQUENCES"):
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_text("Sequences", indent=250)
                        dpg.add_combo(items=[], width=300)
                        dpg.add_button(label="NEW", width=80)
                        dpg.add_button(label="EDIT", width=80)
                        dpg.add_button(label="SEND", width=80)

                    dpg.add_spacer(height=20)
                    with dpg.group(horizontal=True):
                        dpg.add_text("DEVICE", indent=100)
                        dpg.add_text("NAME", indent=300)
                        dpg.add_text("OPERATION", indent=500)
                        dpg.add_text("START AFTER", indent=700)
                        dpg.add_text("PAYLOAD", indent=900)

                    dpg.add_separator()
                    dpg.add_spacer(height=80)

                    dpg.add_text("NO VALID SEQUENCE AVAILABLE\nPLEASE CHANGE THE HARDWARE CONFIG",
                                 color=theme.TEXT_DIM, indent=450)

                # KARTA 4: LOGGER (Przeniesiony terminal z logami)
                with dpg.tab(label="LOGGER"):
                    dpg.add_spacer(height=10)
                    with dpg.group(horizontal=True):
                        dpg.add_text("Ground Station Logs", indent=400)
                        dpg.add_spacer(width=300)
                        dpg.add_text("Log level:")
                        dpg.add_combo(items=["INFO", "DEBUG", "WARNING", "ERROR"], default_value="INFO", width=100)

                    # Tutaj przypisujemy TAG terminal_container, z którego korzysta autoscroll
                    with dpg.child_window(width=-1, height=-1, border=False, tag="terminal_container"):
                        dpg.add_input_text(multiline=True, width=-1, height=-1, readonly=True, tag=self.terminal_id)

            # --- 3. BOTTOM BAR (COMMANDS & TERMINAL CONTROLS) ---
            # Pasek wpisywania komend oraz przyciski obsługi terminala[cite: 11, 14]
            with dpg.child_window(height=50, border=False):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(hint="Enter command to rocket...", width=-350, tag="cmd_input")
                    dpg.add_button(label="SEND", width=80, tag="send_btn")
                    dpg.add_button(label="CLEAR", width=80, tag="clear_btn")
                    dpg.add_checkbox(label="AUTOSCROLL", default_value=True, tag="autoscroll_check")

            # --- 4. MISSION CRITICAL BAR (Poprawka stabilności) ---
            with dpg.child_window(height=50, border=False):
                with dpg.group(horizontal=True):
                    # Grupa lewa
                    with dpg.group(horizontal=True, width=400):
                        dpg.add_button(label="ARM & SYNC", width=130, tag="arm_btn")
                        dpg.add_button(label="DISARM", width=100, tag="disarm_btn")
                        dpg.add_button(label="RESET", width=100, tag="reset_btn")

                    dpg.add_spacer(width=20)
                    dpg.add_text("STATION READY", color=theme.STATUS_GREEN)
                    dpg.add_spacer(width=20)

                    # Grupa prawa (używamy indent, aby przykleić ABORT do prawej strony na 1080p)
                    dpg.add_button(label="DROGUE", width=110, tag="drogue_btn")
                    dpg.add_button(label="MAIN", width=110, tag="main_para_btn")
                    dpg.add_button(label="ABORT", width=90, tag="abort_btn")


    def update_led(self, tag, color):
        """Metoda uaktualniająca kolor kółka rysowanego w Drawlist[cite: 14]."""
        dpg.configure_item(tag, fill=color)