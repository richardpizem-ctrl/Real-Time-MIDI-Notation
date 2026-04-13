import pygame
from typing import Tuple
from ..core.logger import Logger


class TimelineGrid:
    """
    TimelineGrid (Časová os – mriežka)
    ----------------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Vykresľuje beaty a takty na časovej osi
        - Oddelené od TimelineRenderer pre čistú architektúru
        - Pripravené pre PixelLayoutEngine

    Vlastnosti:
        - Real‑time safe
        - Žiadne blokujúce operácie
        - Jednoduché API: render(surface)
    """

    def __init__(
        self,
        width: int,
        height: int,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100,
        beat_color: Tuple[int, int, int] = (90, 90, 90),
        bar_color: Tuple[int, int, int] = (140, 140, 140)
    ) -> None:

        self.width = width
        self.height = height

        self.beats_per_bar = beats_per_bar
        self.pixels_per_beat = pixels_per_beat

        self.beat_color = beat_color
        self.bar_color = bar_color

        # Zoom & offset (doplnene pre TimelineLayoutEngine)
        self.zoom = 1.0
        self.offset_x = 0

        Logger.info("TimelineGrid initialized.")

    # ---------------------------------------------------------
    # EXTERNAL CONTROLS (PixelLayoutEngine / TimelineController)
    # ---------------------------------------------------------
    def set_size(self, width: int, height: int) -> None:
        """Nastaví veľkosť gridu."""
        try:
            self.width = max(1, int(width))
            self.height = max(1, int(height))
        except Exception:
            Logger.error("TimelineGrid set_size error.")

    def set_zoom(self, zoom: float) -> None:
        """Nastaví zoom (ovplyvňuje pixels_per_beat)."""
        try:
            self.zoom = max(0.1, float(zoom))
        except Exception:
            Logger.error("TimelineGrid set_zoom error.")

    def set_offset(self, offset_x: int) -> None:
        """Nastaví horizontálny posun timeline."""
        try:
            self.offset_x = int(offset_x)
        except Exception:
            Logger.error("TimelineGrid set_offset error.")

    # ---------------------------------------------------------
    # RENDER GRID
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        """
        Vykreslí beaty a takty na daný surface (render grid).
        """
        try:
            # Prepočítané PPB podľa zoomu
            scaled_ppb = int(self.pixels_per_beat * self.zoom)

            # -----------------------------
            # BEAT LINES
            # -----------------------------
            # Začíname od prvého beatu, ktorý je viditeľný
            first_visible_beat = max(0, int(self.offset_x // scaled_ppb))

            # Počet beatov, ktoré môžu byť viditeľné
            max_beats = (self.width // scaled_ppb) + 10

            for beat_index in range(first_visible_beat, first_visible_beat + max_beats):
                x = beat_index * scaled_ppb - self.offset_x
                if 0 <= x <= self.width:
                    pygame.draw.line(surface, self.beat_color, (x, 0), (x, self.height))

            # -----------------------------
            # BAR LINES (silnejšie čiary)
            # -----------------------------
            bar_width = self.beats_per_bar * scaled_ppb
            first_visible_bar = max(0, int(self.offset_x // bar_width))
            max_bars = (self.width // bar_width) + 10

            for bar_index in range(first_visible_bar, first_visible_bar + max_bars):
                x = bar_index * bar_width - self.offset_x
                if 0 <= x <= self.width:
                    pygame.draw.line(surface, self.bar_color, (x, 0), (x, self.height), 2)

        except Exception as e:
            Logger.error(f"TimelineGrid render error: {e}")
