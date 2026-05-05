import dearpygui.dearpygui as dpg
from ui.navball import NavballWidget
import ui.theme as theme


class MissionControlLayout:
    def __init__(self):
        self.navball = None
        self.terminal_id = dpg.generate_uuid()

    def create_layout(self):
        # Główny kontener zajmujący całe okno
        with dpg.window(tag="Primary Window", no_title_bar=True, no_move=True, no_resize=True):
            # --- 1. TOP BAR (COMMUNICATION) ---
            with dpg.child_window(height=60, border=False):
                with dpg.group(horizontal=True):
                    dpg.add_text("0.0 kb/s", tag="bitrate_text", color=theme.SKYLINK_TEAL)
                    dpg.add_spacer(width=20)

                    dpg.add_button(label="SCAN", width=80, callback=None)  # Tu wejdzie scan_ports
                    dpg.add_combo(items=[], label="", width=150, tag="port_combo")

                    # Główny status LED (5-kolorowy)
                    with dpg.drawlist(width=30, height=30):
                        dpg.draw_circle((15, 15), 10, color=(50, 50, 50), fill=(0, 0, 0), tag="main_status_led")

                    dpg.add_button(label="OPEN | CLOSE", width=120, tag="connect_btn")
                    dpg.add_button(label="STG", width=40)  # Settings icon placeholder

                    dpg.add_spacer(width=20)
                    # Diody TX / RX
                    with dpg.group():
                        with dpg.group(horizontal=True):
                            dpg.add_text("TX", color=(100, 100, 100), tag="tx_text")
                            with dpg.drawlist(width=15, height=15):
                                dpg.draw_circle((7, 7), 5, fill=(0, 0, 0), tag="tx_led")
                        with dpg.group(horizontal=True):
                            dpg.add_text("RX", color=(100, 100, 100), tag="rx_text")
                            with dpg.drawlist(width=15, height=15):
                                dpg.draw_circle((7, 7), 5, fill=(0, 0, 0), tag="rx_led")

            dpg.add_separator()

            # --- 2. CENTER SECTION (TELEMETRY & NAVBALL) ---
            with dpg.group(horizontal=True):
                # Lewa strona: Telemetry Feed (Terminal)
                with dpg.child_window(width=-400, border=True):
                    dpg.add_text("TELEMETRY FEED", color=theme.SKYLINK_TEAL)
                    dpg.add_input_text(
                        multiline=True,
                        width=-1,
                        height=-1,
                        readonly=True,
                        tag=self.terminal_id,
                        tab_input=True
                    )

                # Prawa strona: Navigation & Rocket State
                with dpg.child_window(width=400, border=True):
                    dpg.add_text("NAVIGATION", indent=140, color=theme.SKYLINK_TEAL)

                    # Kontener na Navball
                    nav_container = dpg.add_child_window(height=350, border=False)
                    self.navball = NavballWidget(nav_container)

                    dpg.add_separator()
                    dpg.add_text("FLIGHT DATA", color=theme.SKYLINK_TEAL)
                    dpg.add_text("STATE: IDLE", tag="state_display")  # Zgodnie z FSM
                    dpg.add_text("ALTITUDE: 0.0 m", tag="alt_display")
                    dpg.add_text("VOLTAGE: 0.0 V", tag="volt_display")  # Monitorowanie 18650

            # --- 3. BOTTOM BAR (COMMANDS) ---
            with dpg.child_window(height=50, border=False):
                with dpg.group(horizontal=True):
                    dpg.add_input_text(hint="Enter command to rocket...", width=-300, tag="cmd_input")
                    dpg.add_button(label="SEND", width=80)
                    dpg.add_button(label="CLEAR", width=80)
                    dpg.add_checkbox(label="AUTOSCROLL", default_value=True)

    def update_led(self, tag, color):
        """Pomocnicza metoda do zmiany koloru LEDów."""
        dpg.configure_item(tag, fill=color)