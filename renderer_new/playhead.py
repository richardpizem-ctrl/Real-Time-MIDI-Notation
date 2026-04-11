import pygame
from typing import Tuple
from ..core.logger import Logger


class Playhead:
    """
    Playhead (Prehrávacia hlava)
    ----------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Reprezentuje vertikálnu čiaru ukazujúcu aktuálnu pozíciu prehrávania
        - Používa sa v timeline aj v grafickej notácii
        - Oddelená logika pre výpočet pozície a vykreslenie

    Vlastnosti:
        - Real‑time safe
        - Neobsahuje žiadne blokujúce operácie
        - Pripravené pre PixelLayoutEngine
    """

    def __init__(
        self,
        height: int,
        color: Tuple[int, int, int] = (255, 80, 80),
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        self.height = height
        self.color = color

        self.bpm = bpm
        self.beats_per_bar = beats_per_bar
        self.pixels_per_beat = pixels_per_beat

        self.x = 0  # aktuálna pozícia playheadu v pixeloch

        Logger.info("Playhead initialized.")

    # ---------------------------------------------------------
    # UPDATE POSITION
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """
        Aktualizuje pozíciu playheadu podľa času (update playhead position).
        """
        try:
            beats_per_second = self.bpm / 60.0
            total_beats = time_seconds * beats_per_second

            # Prepočet na pixely
            self.x = int(total_beats * self.pixels_per_beat)

        except Exception as e:
            Logger.error(f"Playhead update error: {e}")

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        """
        Vykreslí playhead na daný surface (render playhead).
        """
        try:
            pygame.draw.line(
                surface,
                self.color,
                (self.x, 0),
                (self.x, self.height),
                2
            )
        except Exception as e:
            Logger.error(f"Playhead render error: {e}")

