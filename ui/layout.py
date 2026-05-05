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
                with dpg.tab(label="HARDWARE"):
                    with dpg.group(horizontal=True):
                        # Lewa strona: Telemetry Feed
                        with dpg.child_window(width=-420, border=True, tag="terminal_container"):  # Dodaj tag tutaj
                            dpg.add_text("TELEMETRY FEED", color=theme.SKYLINK_TEAL)
                            dpg.add_input_text(multiline=True, width=-1, height=-1, readonly=True, tag=self.terminal_id)

                        # Prawa strona: Navball & Flight Metrics
                        with dpg.child_window(width=410, border=True):
                            nav_container = dpg.add_child_window(height=350, border=False)
                            self.navball = NavballWidget(nav_container)
                            dpg.add_separator()
                            dpg.add_text("STATE: IDLE", tag="state_display")
                            dpg.add_text("ALTITUDE: 0.0 m", tag="alt_display")
                            dpg.add_text("VOLTAGE: 0.0 V", tag="volt_display")

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

            # --- 3. BOTTOM BAR (COMMANDS & TERMINAL CONTROLS) ---
            # Pasek wpisywania komend oraz przyciski obsługi terminala[cite: 11, 14]
            with dpg.child_window(height=50, border=False):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(hint="Enter command to rocket...", width=-350, tag="cmd_input")
                    dpg.add_button(label="SEND", width=80, tag="send_btn")
                    dpg.add_button(label="CLEAR", width=80, tag="clear_btn")
                    dpg.add_checkbox(label="AUTOSCROLL", default_value=True, tag="autoscroll_check")

            # --- 4. MISSION CRITICAL BAR (BOTTOM BUTTONS) ---
            # Odzwierciedlenie kolorowych przycisków z Twojego raportu
            with dpg.child_window(height=45, border=False):
                with dpg.group(horizontal=True):
                    # ARM & SYNC (Usuwamy 'color=')
                    arm_btn = dpg.add_button(label="ARM & SYNC", width=150, tag="arm_btn")
                    dpg.bind_item_theme(arm_btn, theme.create_button_theme(theme.STATUS_BLUE))

                    # DISARM
                    disarm_btn = dpg.add_button(label="DISARM", width=120, tag="disarm_btn")
                    dpg.bind_item_theme(disarm_btn, theme.create_button_theme(theme.STATUS_AMBER))

                    # RESET
                    reset_btn = dpg.add_button(label="RESET DYNAMIXELS", width=180, tag="reset_btn")
                    dpg.bind_item_theme(reset_btn, theme.create_button_theme(theme.STATUS_RED))

                    dpg.add_spacer(width=20)
                    dpg.add_text("SYSTEM READY", tag="status_msg_text", color=theme.STATUS_GREEN)

                    dpg.add_spacer(width=20)

                    dpg.add_button(label="DEPLOY DROGUE", width=140, tag="drogue_btn")
                    dpg.add_button(label="DEPLOY MAIN", width=140, tag="main_para_btn")

                    # ABORT
                    abort_btn = dpg.add_button(label="ABORT", width=100, tag="abort_btn")
                    dpg.bind_item_theme(abort_btn, theme.create_button_theme(theme.STATUS_RED))

    def update_led(self, tag, color):
        """Metoda uaktualniająca kolor kółka rysowanego w Drawlist[cite: 14]."""
        dpg.configure_item(tag, fill=color)