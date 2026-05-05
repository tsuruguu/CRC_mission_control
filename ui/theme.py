import dearpygui.dearpygui as dpg

# Definicja palety kolorów Skylink (RGBA)
SKYLINK_TEAL = (0, 168, 150, 255)
SKYLINK_TEAL_TRANSPARENT = (0, 168, 150, 100)
BG_DARK = (11, 14, 20, 255)  # #0B0E14
BG_SECONDARY = (20, 25, 35, 255)  # Nieco jaśniejsze dla sekcji
TEXT_MAIN = (224, 224, 224, 255)  # #E0E0E0

# Kolory statusów
STATUS_GREEN = (0, 255, 0, 255)
STATUS_RED = (255, 0, 0, 255)
STATUS_AMBER = (255, 191, 0, 255)
STATUS_BLUE = (0, 120, 255, 255)


def apply_skylink_theme():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            # --- KOLORY ---
            # Tło okien i paneli[cite: 1]
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, BG_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BG_SECONDARY)
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, BG_SECONDARY)
            dpg.add_theme_color(dpg.mvThemeCol_Border, SKYLINK_TEAL_TRANSPARENT)

            # Tekst[cite: 1]
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_MAIN)

            # Nagłówki i Tytuły okien
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, SKYLINK_TEAL)
            dpg.add_theme_color(dpg.mvThemeCol_Header, SKYLINK_TEAL_TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, SKYLINK_TEAL)

            # Przyciski
            dpg.add_theme_color(dpg.mvThemeCol_Button, SKYLINK_TEAL_TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SKYLINK_TEAL)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (0, 200, 180, 255))

            # Pola Input (Terminal / Suwaki)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, (30, 35, 45, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (40, 45, 55, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, SKYLINK_TEAL_TRANSPARENT)

            # --- STYLIZACJA (NASA LOOK) ---
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)  # Nowoczesne zaokrąglenia
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 12, 12)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 8, 8)  # Przejrzysty układ
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 12)

    dpg.bind_theme(global_theme)


def setup_fonts():
    """Ładowanie nowoczesnych fontów."""
    # Załóżmy, że wrzucisz te pliki do assets/fonts/
    with dpg.font_registry():
        try:
            # Inter dla interfejsu (czysty, nowoczesny)
            default_font = dpg.add_font("assets/fonts/Inter-Regular.ttf", 16)
            # JetBrains Mono dla terminala i danych telemetrii (czytelność liczb)
            mono_font = dpg.add_font("assets/fonts/JetBrainsMono-Bold.ttf", 14)

            dpg.bind_font(default_font)
            return mono_font
        except Exception:
            print("Font files not found. Using default DPG font.")
            return None