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

        Logger.info("TimelineGrid initialized.")

    # ---------------------------------------------------------
    # RENDER GRID
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        """
        Vykreslí beaty a takty na daný surface (render grid).
        """
        try:
            # Beat = každých X pixelov
            for x in range(0, self.width, self.pixels_per_beat):
                pygame.draw.line(surface, self.beat_color, (x, 0), (x, self.height))

            # Takt = každé beats_per_bar * pixels_per_beat
            bar_width = self.beats_per_bar * self.pixels_per_beat

            for x in range(0, self.width, bar_width):
                pygame.draw.line(surface, self.bar_color, (x, 0), (x, self.height), 2)

        except Exception as e:
            Logger.error(f"TimelineGrid render error: {e}")

