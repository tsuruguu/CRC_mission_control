import dearpygui.dearpygui as dpg
from ui.theme import apply_skylink_theme

dpg.create_context()
dpg.create_viewport(title='FST AGH - Mission Control v2', width=1280, height=720)

with dpg.window(tag="Primary Window"):
    # TOP BAR
    with dpg.group(horizontal=True):
        dpg.add_text("0.0 kb/s", color=(0, 168, 150))
        dpg.add_button(label="SCAN", callback=None)  # Tutaj podepniesz serial_manager
        dpg.add_combo(items=["COM1", "COM2"], label="Port")
        dpg.add_button(label="OPEN|CLOSE", color=(0, 200, 0))

    dpg.add_separator()

    # MAIN CONTENT
    with dpg.group(horizontal=True):
        # Telemetry Feed
        dpg.add_input_text(multiline=True, width=800, height=500, readonly=True, tag="telemetry_log")

        # Navball Placeholder
        with dpg.child_window(width=400):
            dpg.add_text("NAVIGATION", indent=150)
            with dpg.drawlist(width=300, height=300):
                dpg.draw_circle((150, 150), 140, color=(0, 168, 150), thickness=2)
                # Tu wejdzie Twoja kula z navballa

apply_skylink_theme()  # Twoja funkcja z kolorami

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.set_primary_window("Primary Window", True)
dpg.start_dearpygui()
dpg.destroy_context()