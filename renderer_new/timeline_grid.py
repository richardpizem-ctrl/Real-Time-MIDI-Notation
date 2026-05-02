# =========================================================
# TimelineGrid v2.0.0
# Stabilná mriežka pre timeline (beaty + takty)
# =========================================================

import pygame
from typing import Tuple
from ..core.logger import Logger


class TimelineGrid:
    """
    TimelineGrid (v2.0.0)
    ---------------------
    Účel:
        - Vykresľuje beaty a takty na časovej osi
        - Oddelené od TimelineController pre čistú architektúru
        - Pripravené pre PixelLayoutEngine (v3)

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

        try:
            self.width = int(width)
        except Exception:
            self.width = 1600

        try:
            self.height = int(height)
        except Exception:
            self.height = 120

        self.beats_per_bar = max(1, int(beats_per_bar))
        self.pixels_per_beat = max(1, int(pixels_per_beat))

        self.beat_color = beat_color
        self.bar_color = bar_color

        # Zoom & offset (pre TimelineLayoutEngine)
        self.zoom = 1.0
        self.offset_x = 0

        Logger.info("TimelineGrid initialized (v2.0.0).")

    # ---------------------------------------------------------
    # EXTERNAL CONTROLS
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
        Vykreslí beaty a takty na daný surface.
        Real‑time safe.
        """
        if surface is None:
            return

        try:
            # Prepočítané PPB podľa zoomu
            scaled_ppb = int(self.pixels_per_beat * self.zoom)
            if scaled_ppb <= 0:
                return

            # -----------------------------
            # BEAT LINES
            # -----------------------------
            first_visible_beat = max(0, int(self.offset_x // scaled_ppb))
            max_beats = (self.width // scaled_ppb) + 10

            for beat_index in range(first_visible_beat, first_visible_beat + max_beats):
                x = beat_index * scaled_ppb - self.offset_x
                if 0 <= x <= self.width:
                    pygame.draw.line(surface, self.beat_color, (x, 0), (x, self.height))

            # -----------------------------
            # BAR LINES (silnejšie čiary)
            # -----------------------------
            bar_width = self.beats_per_bar * scaled_ppb
            if bar_width <= 0:
                return

            first_visible_bar = max(0, int(self.offset_x // bar_width))
            max_bars = (self.width // bar_width) + 10

            for bar_index in range(first_visible_bar, first_visible_bar + max_bars):
                x = bar_index * bar_width - self.offset_x
                if 0 <= x <= self.width:
                    pygame.draw.line(surface, self.bar_color, (x, 0), (x, self.height), 2)

        except Exception as e:
            Logger.error(f"TimelineGrid render error: {e}")
