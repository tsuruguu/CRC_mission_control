import dearpygui.dearpygui as dpg
import logging

# --- PALETA KOLORÓW SKYLINK AGH ---
SKYLINK_TEAL = (0, 168, 150, 255)
SKYLINK_TEAL_TRANSPARENT = (0, 168, 150, 80)
SKYLINK_TEAL_BRIGHT = (0, 210, 190, 255)

# Tło i Warstwy (Dark Space Theme)
BG_DARK = (11, 14, 20, 255)  # Główny panel
BG_SECONDARY = (20, 25, 35, 255)  # Panele boczne (Child Windows)
BG_WIDGET = (30, 38, 50, 255)  # Tło pól tekstowych i przycisków

# Typografia i Statusy
TEXT_MAIN = (224, 224, 224, 255)  # Jasny szary[cite: 12]
TEXT_DIM = (160, 160, 160, 255)  # Podpisy pomocnicze

STATUS_GREEN = (46, 204, 113, 255)
STATUS_RED = (231, 76, 60, 255)
STATUS_AMBER = (241, 196, 15, 255)
STATUS_BLUE = (52, 152, 219, 255)


def apply_skylink_theme():
    """Konfiguruje globalny styl graficzny stacji naziemnej[cite: 12]."""
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            # --- KOLORYSTYKA ---
            # Okna i Panele
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, BG_DARK)
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, BG_SECONDARY)
            dpg.add_theme_color(dpg.mvThemeCol_Border, SKYLINK_TEAL_TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_Separator, SKYLINK_TEAL_TRANSPARENT)

            # Tekst i Nagłówki
            dpg.add_theme_color(dpg.mvThemeCol_Text, TEXT_MAIN)
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, SKYLINK_TEAL)
            dpg.add_theme_color(dpg.mvThemeCol_Header, SKYLINK_TEAL_TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, SKYLINK_TEAL)

            # Elementy Interaktywne (Przyciski, Checkboxy)
            dpg.add_theme_color(dpg.mvThemeCol_Button, SKYLINK_TEAL_TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, SKYLINK_TEAL)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, SKYLINK_TEAL_BRIGHT)
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, SKYLINK_TEAL_BRIGHT)

            # Pola wprowadzania (Terminal / Komendy)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, BG_WIDGET)
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, (45, 55, 75, 255))
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, (50, 65, 90, 255))

            # Scrollbar (Inżynieryjny look)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, SKYLINK_TEAL_TRANSPARENT)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, SKYLINK_TEAL)
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, SKYLINK_TEAL_BRIGHT)

            # --- GEOMETRIA I STYL (NASA MODERN) ---
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)  # Zaokrąglenia[cite: 12]
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)  # Większa spójność
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 4)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 15, 15)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)  # Więcej oddechu
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarSize, 12)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 12)
            dpg.add_theme_style(dpg.mvStyleVar_SeparatorTextPadding, 10, 10)

    dpg.bind_theme(global_theme)


import logging  # <--- DODAJ IMPORT


def setup_fonts():
    logger = logging.getLogger("MissionControl")  # <--- POBIERZ LOGGER[cite: 21]
    with dpg.font_registry():
        try:
            # Próba załadowania fontów[cite: 16]
            default_font = dpg.add_font("assets/fonts/Inter-Regular.ttf", 16)

            with dpg.font(default_font):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range(0xf000, 0xf8ff)
                dpg.add_font("assets/fonts/fa-solid-900.otf", 16)

            mono_font = dpg.add_font("assets/fonts/JetBrainsMono-Bold.ttf", 14)

            dpg.bind_font(default_font)
            logger.info("UI Fonts loaded successfully")  # <--- LOG SUKCESU[cite: 21]
            return mono_font
        except Exception as e:
            logger.error(f"KRYTYCZNY BŁĄD CZCIONEK: {e}")  # <--- LOG BŁĘDU[cite: 21]
            return None