import dearpygui.dearpygui as dpg
import math


class NavballWidget:
    def __init__(self, parent_tag, width=350, height=350):
        self.width = width
        self.height = height
        self.center_x = width / 2
        self.center_y = height / 2
        self.radius = 100

        # Kolory zgodne z Twoim zdjęciem i stylem Skylink
        self.sky_color = (41, 128, 185, 255)  # Niebieski (niebo)
        self.ground_color = (15, 15, 15, 255)  # Prawie czarny (ziemia)
        self.line_color = (255, 255, 255, 200)  # Biały
        self.accent_color = (255, 191, 0, 255)  # Żółty/Bursztynowy dla znaczników
        self.bg_color = (11, 14, 20, 255)  # Tło takie samo jak okno (z theme.py)

        # Unikalne ID (tagi) dla elementów, które będą się poruszać
        self.horizon_node = dpg.generate_uuid()
        self.pitch_indicator = dpg.generate_uuid()
        self.roll_indicator = dpg.generate_uuid()
        self.yaw_indicator = dpg.generate_uuid()

        # Renderowanie Navballa
        self._build_ui(parent_tag)

    def _build_ui(self, parent_tag):
        with dpg.drawlist(width=self.width, height=self.height, parent=parent_tag):
            # --- 1. SFERA NAVBALLA (OBRACAJĄCY SIĘ WĘZEŁ GPU) ---
            with dpg.draw_node(tag=self.horizon_node):
                # Rysujemy ogromne prostokąty z punktem zerowym w środku (0,0)
                # Niebo (Górna połowa)
                dpg.draw_rectangle((-300, -300), (300, 0), color=self.sky_color, fill=self.sky_color)
                # Ziemia (Dolna połowa)
                dpg.draw_rectangle((-300, 0), (300, 300), color=self.ground_color, fill=self.ground_color)
                # Linia horyzontu
                dpg.draw_line((-300, 0), (300, 0), color=self.line_color, thickness=2)

            # --- 2. MASKA ("DONUT TRICK") ---
            # To jest trik, który wycina nam z wielkich obracających się prostokątów idealne koło.
            # Rysujemy bardzo gruby pierścień w kolorze tła, który przykrywa rogi prostokątów.
            mask_thickness = 150
            mask_radius = self.radius + (mask_thickness / 2)
            dpg.draw_circle((self.center_x, self.center_y), mask_radius, color=self.bg_color, thickness=mask_thickness)

            # Ramka Navballa
            dpg.draw_circle((self.center_x, self.center_y), self.radius, color=self.line_color, thickness=2)

            # --- 3. ŚRODKOWY CELOWNIK (Crosshair) ---
            # Dokładnie taki, jak na PFD (Primary Flight Display) w lotnictwie
            c_x, c_y = self.center_x, self.center_y
            dpg.draw_line((c_x - 30, c_y), (c_x - 10, c_y), color=self.accent_color, thickness=3)
            dpg.draw_line((c_x + 10, c_y), (c_x + 30, c_y), color=self.accent_color, thickness=3)
            dpg.draw_circle((c_x, c_y), 3, color=self.accent_color, fill=self.accent_color)

            # --- 4. SUWAKI Z KULKAMI Z TWOJEGO RYSUNKU ---
            # Górny suwak (Yaw / Wychylenie)
            dpg.draw_rectangle((c_x - 80, c_y - 140), (c_x + 80, c_y - 130), color=self.line_color)
            dpg.draw_circle((c_x, c_y - 135), 6, color=self.accent_color, fill=self.accent_color,
                            tag=self.yaw_indicator)

            # Lewy suwak (Pitch / Pochylenie)
            dpg.draw_rectangle((c_x - 140, c_y - 80), (c_x - 130, c_y + 80), color=self.line_color)
            dpg.draw_circle((c_x - 135, c_y), 6, color=self.accent_color, fill=self.accent_color,
                            tag=self.pitch_indicator)

            # Prawy suwak (Roll / Przechylenie)
            dpg.draw_rectangle((c_x + 130, c_y - 80), (c_x + 140, c_y + 80), color=self.line_color)
            dpg.draw_circle((c_x + 135, c_y), 6, color=self.accent_color, fill=self.accent_color,
                            tag=self.roll_indicator)

    def update(self, pitch: float, roll: float, yaw: float):
        """
        Główna metoda uaktualniająca pozycje na podstawie danych z telemetrii.
        pitch: -90 do 90 (Nose down / Nose up)
        roll: -180 do 180
        yaw: -180 do 180
        """
        # --- 1. OBRÓT KULI NAVBALLA (GPU MATRICES) ---
        # Pitch przesuwa horyzont góra/dół. Roll go obraca.
        # ImGui wymaga użycia macierzy (to robi robotę sprzętowo!)

        # Jeśli rakieta podnosi dziób (pitch > 0), horyzont opada
        pitch_pixels = (pitch / 90.0) * self.radius

        # Macierze: przesunięcie na środek -> obrót -> pochylenie
        rot_mat = dpg.create_rotation_matrix(math.radians(roll), [0, 0, -1])
        trans_center = dpg.create_translation_matrix([self.center_x, self.center_y])
        trans_pitch = dpg.create_translation_matrix([0, pitch_pixels])

        # Nakładamy zoptymalizowaną macierz na nasz węzeł rysowania
        final_matrix = trans_center * rot_mat * trans_pitch
        dpg.apply_transform(self.horizon_node, final_matrix)

        # --- 2. RUCH KULEK NA SUWAKACH ---
        # Aktualizacja Yaw (lewo-prawo)
        yaw_x = self.center_x + (yaw / 180.0) * 80
        yaw_x = max(self.center_x - 80, min(self.center_x + 80, yaw_x))  # Blokada wyjścia poza suwak
        dpg.configure_item(self.yaw_indicator, center=(yaw_x, self.center_y - 135))

        # Aktualizacja Pitch (góra-dół na lewym suwaku)
        pitch_y = self.center_y - (pitch / 90.0) * 80
        pitch_y = max(self.center_y - 80, min(self.center_y + 80, pitch_y))
        dpg.configure_item(self.pitch_indicator, center=(self.center_x - 135, pitch_y))

        # Aktualizacja Roll (góra-dół na prawym suwaku)
        roll_y = self.center_y - (roll / 180.0) * 80
        roll_y = max(self.center_y - 80, min(self.center_y + 80, roll_y))
        dpg.configure_item(self.roll_indicator, center=(self.center_x + 135, roll_y))