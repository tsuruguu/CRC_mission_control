import dearpygui.dearpygui as dpg
from ui.navball import NavballWidget
import ui.theme as theme


class MissionControlLayout:
    def __init__(self):
        self.navball = None
        self.terminal_id = "telemetry_feed_terminal"

    def create_layout(self):
        # Główny kontener Viewportu - wyłączamy scrollbar dla całego okna
        with dpg.window(tag="Primary Window", no_title_bar=True, no_move=True,
                        no_resize=True, no_scrollbar=True):
            # --- 1. TOP BAR (Stała wysokość: 60px) ---
            with dpg.child_window(height=60, border=False, no_scrollbar=True):
                with dpg.group(horizontal=True):
                    dpg.add_text("0.0 kb/s", tag="bitrate_text", color=theme.ACCENT_PRIMARY)
                    dpg.add_spacer(width=20)
                    dpg.add_button(label="SCAN", width=80, tag="scan_btn")
                    dpg.add_combo(items=[], label="", width=150, tag="port_combo")
                    with dpg.drawlist(width=30, height=30):
                        dpg.draw_circle((15, 15), 10, color=theme.ACCENT_TRANS, fill=theme.COLOR_BLACK,
                                        tag="main_status_led")
                    dpg.add_button(label="OPEN | CLOSE", width=120, tag="connect_btn")
                    dpg.add_button(label="STG", width=40, tag="settings_btn")
                    dpg.add_spacer(width=20)
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            dpg.add_text("TX", color=theme.TEXT_NORMAL)
                            with dpg.drawlist(width=15, height=15):
                                dpg.draw_circle((7, 7), 5, fill=theme.COLOR_BLACK, tag="tx_led")
                        with dpg.group(horizontal=True):
                            dpg.add_text("RX", color=theme.TEXT_NORMAL)
                            with dpg.drawlist(width=15, height=15):
                                dpg.draw_circle((7, 7), 5, fill=theme.COLOR_BLACK, tag="rx_led")

            dpg.add_separator()

            # --- 2. ŚRODKOWY OBSZAR ROBOCZY (Dynamiczna wysokość) ---
            with dpg.child_window(height=-110, border=False, tag="main_content_area"):
                with dpg.tab_bar():
                    # KARTA: COMMUNICATION
                    # ui/layout.py - Fragment zakładki COMMUNICATION
                    with dpg.tab(label="COMMUNICATION"):
                        with dpg.group(horizontal=True):
                            # Lewa kolumna: Terminale
                            with dpg.child_window(width=-400, border=True):
                                # RAW TELEMETRY FEED
                                with dpg.group(horizontal=True):
                                    dpg.add_text("TELEMETRY FEED (RAW)", color=theme.ACCENT_PRIMARY)
                                    dpg.add_spacer(width=20)
                                    dpg.add_checkbox(label="AUTO", default_value=True, tag="raw_autoscroll_check")
                                    dpg.add_button(label="CLEAR", tag="clear_raw_btn", small=True)

                                with dpg.child_window(height=350, border=True, tag="raw_feed_container"):
                                    dpg.add_text("", tag="raw_telemetry_feed")

                                dpg.add_spacer(height=10)
                                dpg.add_separator()

                                # COMMAND CONSOLE
                                with dpg.group(horizontal=True):
                                    dpg.add_text("COMMAND CONSOLE", color=theme.STATUS_BLUE)
                                    dpg.add_spacer(width=35)
                                    dpg.add_checkbox(label="AUTO", default_value=True, tag="cmd_autoscroll_check")
                                    dpg.add_button(label="CLEAR", tag="clear_cmd_btn", small=True)

                                with dpg.child_window(height=-1, border=True, tag="command_console_container"):
                                    dpg.add_text("", tag="command_console")

                            # Prawa kolumna: Navball i Wskaźniki
                            with dpg.child_window(width=380, border=True):
                                nav_container = dpg.add_child_window(height=350, border=False)
                                self.navball = NavballWidget(nav_container)
                                dpg.add_separator()
                                dpg.add_text("STATE: IDLE", tag="state_display")
                                dpg.add_text("ALTITUDE: 0.0 m", tag="alt_display")
                                dpg.add_text("PAYLOAD TEMP: 0.0 °C", tag="temp_display")
                                dpg.add_text("VOLTAGE: 0.0 V", tag="volt_display")

                    # KARTA: PAYLOAD
                    with dpg.tab(label="PAYLOAD"):
                        dpg.add_spacer(height=10)
                        dpg.add_text("ALGAE BIOLOGICAL PAYLOAD MONITOR", indent=550, color=theme.ACCENT_PRIMARY)
                        with dpg.group(horizontal=True):
                            with dpg.child_window(width=400, height=150, border=False):
                                dpg.add_text("CURRENT TEMP", color=theme.TEXT_NORMAL)
                                dpg.add_text("20.0 °C", tag="big_temp_val", color=theme.STATUS_AMBER)
                                dpg.bind_item_font("big_temp_val", "big_payload_font")
                            with dpg.child_window(width=400, height=150, border=False):
                                dpg.add_text("UV INTENSITY", color=theme.TEXT_NORMAL)
                                dpg.add_text("0", tag="big_uv_val", color=theme.STATUS_BLUE)
                                dpg.bind_item_font("big_uv_val", "big_payload_font")
                        with dpg.plot(height=-1, width=-1):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="Time (s)", tag="temp_x_axis")
                            y_axis = dpg.add_plot_axis(dpg.mvYAxis, label="Temp (°C)", tag="temp_y_axis")
                            dpg.add_line_series([], [], label="Temp Trend", parent=y_axis, tag="temp_plot_series")

                    # KARTA: HARDWARE
                    with dpg.tab(label="HARDWARE"):
                        with dpg.child_window(width=-1, height=-1, border=False, horizontal_scrollbar=True):
                            with dpg.group(horizontal=True):
                                dpg.add_text("Crc 2026 Rocket Hardware", color=theme.ACCENT_PRIMARY)
                                dpg.add_spacer(width=50)
                                dpg.add_button(label="Maintenance", width=120)
                                dpg.add_button(label="Snapshot", width=100)

                            dpg.add_spacer(height=10)
                            with dpg.group(horizontal=True):
                                panel_w, panel_h = 125, 220

                                # Panele sensorów
                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("IMU_MPU9250", color=theme.TEXT_NORMAL)
                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("BARO_BMP280", color=theme.TEXT_NORMAL)
                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("GPS_GP02", color=theme.TEXT_NORMAL)
                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("BODY_STRESS", color=theme.TEXT_NORMAL)

                                # Kontrola mechanizmów
                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("AERO_FINS", color=theme.TEXT_NORMAL)
                                    dpg.add_spacer(height=20)
                                    dpg.add_text("0", indent=55)
                                    dpg.add_input_text(width=-1, default_value="--")
                                    dpg.add_button(label="SET", width=-1)
                                    dpg.add_spacer(height=10)
                                    dpg.add_button(label="OPEN", width=-1)
                                    dpg.add_button(label="CLOSE", width=-1)

                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("RECOVERY_SYS", color=theme.TEXT_NORMAL)
                                    dpg.add_text("ARMED", color=theme.TEXT_NORMAL)
                                    dpg.add_spacer(height=30)
                                    dpg.add_button(label="ARM", width=-1)
                                    dpg.add_button(label="DISARM", width=-1)

                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("BATTERY", color=theme.TEXT_NORMAL)
                                    dpg.add_spacer(height=50)
                                    dpg.add_button(label="OPEN", width=-1)
                                    dpg.add_button(label="CLOSE", width=-1)

                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("SD_LOGGER", color=theme.TEXT_NORMAL)
                                    dpg.add_spacer(height=25)
                                    dpg.add_button(label="START", width=-1)
                                    dpg.add_button(label="STOP", width=-1)
                                    dpg.add_button(label="ERASE", width=-1)

                                with dpg.child_window(width=panel_w, height=panel_h, border=True):
                                    dpg.add_text("BUZZER_LEDS", color=theme.TEXT_NORMAL)
                                    dpg.add_spacer(height=50)
                                    dpg.add_button(label="OPEN", width=-1)
                                    dpg.add_button(label="CLOSE", width=-1)

                                with dpg.child_window(width=panel_w + 15, height=panel_h, border=True):
                                    dpg.add_text("FLIGHT_SCHED", color=theme.TEXT_NORMAL)
                                    dpg.add_text("Seq State Unk", color=theme.TEXT_NORMAL, wrap=120)
                                    dpg.add_spacer(height=10)
                                    with dpg.group(horizontal=True):
                                        dpg.add_button(label="START", width=60)
                                        dpg.add_button(label="CLEAR", width=60)

                    # KARTA: SEQUENCES
                    with dpg.tab(label="SEQUENCES"):
                        dpg.add_spacer(height=10)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Sequences", indent=250)
                            dpg.add_combo(items=[], width=300)
                            dpg.add_button(label="NEW", width=80)
                            dpg.add_button(label="EDIT", width=80)
                            dpg.add_button(label="SEND", width=80)
                        dpg.add_spacer(height=20)
                        dpg.add_text("NO VALID SEQUENCE AVAILABLE\nPLEASE CHANGE THE HARDWARE CONFIG",
                                     color=theme.TEXT_NORMAL, indent=450)

                    # KARTA: LOGGER
                    with dpg.tab(label="LOGGER"):
                        dpg.add_spacer(height=10)
                        with dpg.group(horizontal=True):
                            dpg.add_text("Ground Station Logs", indent=400)
                            dpg.add_spacer(width=300)
                            dpg.add_text("Log level:")
                            dpg.add_combo(items=["INFO", "DEBUG", "WARNING", "ERROR"], default_value="INFO", width=100)
                        with dpg.child_window(width=-1, height=-1, border=False, tag="terminal_container"):
                            dpg.add_text("", tag=self.terminal_id)

            dpg.add_separator()

            # --- 3. PRZYKLEJONY PANEL DOLNY ---
            with dpg.group(tag="fixed_bottom_panel"):
                # Pasek komend (zmniejszone szerokości dla lepszego pasowania)
                with dpg.child_window(height=45, border=False, no_scrollbar=True):
                    with dpg.group(horizontal=True):
                        dpg.add_input_text(hint="Enter command to rocket...", width=-280, tag="cmd_input")
                        dpg.add_button(label="SEND", width=75, tag="send_btn")
                        dpg.add_button(label="CLEAR", width=75, tag="clear_btn")
                        dpg.add_checkbox(label="AUTO", default_value=True, tag="autoscroll_check")

                # Pasek Mission Critical
                with dpg.child_window(height=50, border=False, no_scrollbar=True):
                    # TWORZYMY JEDEN WSPÓLNY MOTYW DLA WSZYSTKICH PRZYCISKÓW (MORSKI #096C6C)
                    action_theme = theme.create_button_theme(theme.COLOR_TEAL)

                    with dpg.group(horizontal=True):
                        # Przyciski kontrolne - wszystkie w tym samym kolorze
                        arm_btn = dpg.add_button(label="ARM & SYNC", width=110, tag="arm_btn")
                        disarm_btn = dpg.add_button(label="DISARM", width=90, tag="disarm_btn")
                        reset_btn = dpg.add_button(label="RESET", width=80, tag="reset_btn")

                        dpg.add_spacer(width=10)
                        dpg.add_text("STATION READY", color=theme.TEXT_NORMAL)
                        dpg.add_spacer(width=10)

                        drogue_btn = dpg.add_button(label="DROGUE", width=90, tag="drogue_btn")
                        main_btn = dpg.add_button(label="MAIN", width=90, tag="main_para_btn")
                        abort_btn = dpg.add_button(label="ABORT", width=80, tag="abort_btn")

                        # BINDOWANIE JEDNEGO MOTYWU DO WSZYSTKICH PRZYCISKÓW
                        dpg.bind_item_theme(arm_btn, action_theme)
                        dpg.bind_item_theme(disarm_btn, action_theme)
                        dpg.bind_item_theme(reset_btn, action_theme)
                        dpg.bind_item_theme(drogue_btn, action_theme)
                        dpg.bind_item_theme(main_btn, action_theme)
                        dpg.bind_item_theme(abort_btn, action_theme)


    def update_led(self, tag, color):
        """Metoda uaktualniająca kolor kółka rysowanego w Drawlist."""
        dpg.configure_item(tag, fill=color)