import pygame
from typing import Tuple, Optional
from ..core.logger import Logger


class TimelineRenderer:
    """
    TimelineRenderer (Časová os)
    ----------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Vykresľuje časovú os projektu
        - Zobrazuje takty, beaty, grid a playhead
        - Slúži ako základ pre PixelLayoutEngine
        - Používa sa v real‑time prehrávaní aj v editácii

    Vlastnosti:
        - Real‑time safe
        - Neobsahuje žiadne blokujúce operácie
        - Oddelená logika pre grid, playhead a layout
    """

    def __init__(
        self,
        width: int,
        height: int = 120,
        bg_color: Tuple[int, int, int] = (25, 25, 25),
        grid_color: Tuple[int, int, int] = (60, 60, 60),
        beat_color: Tuple[int, int, int] = (90, 90, 90),
        playhead_color: Tuple[int, int, int] = (255, 80, 80),
        bpm: float = 120.0,
        beats_per_bar: int = 4
    ) -> None:

        self.width = width
        self.height = height

        self.bg_color = bg_color
        self.grid_color = grid_color
        self.beat_color = beat_color
        self.playhead_color = playhead_color

        self.bpm = bpm
        self.beats_per_bar = beats_per_bar

        self.surface = pygame.Surface((self.width, self.height))
        self.playhead_x = 0

        Logger.info("TimelineRenderer initialized.")

    # ---------------------------------------------------------
    # UPDATE PLAYHEAD POSITION
    # ---------------------------------------------------------
    def update_playhead(self, time_seconds: float) -> None:
        """
        Aktualizuje pozíciu playheadu podľa času (update playhead position).
        """
        try:
            beats_per_second = self.bpm / 60.0
            total_beats = time_seconds * beats_per_second

            # 1 beat = 100 px (nateraz, PixelLayoutEngine to neskôr preberie)
            self.playhead_x = int(total_beats * 100) % self.width

        except Exception as e:
            Logger.error(f"TimelineRenderer update error: {e}")

    # ---------------------------------------------------------
    # RENDER GRID
    # ---------------------------------------------------------
    def _render_grid(self) -> None:
        """Vykreslí grid taktov a beatov (render grid)."""
        try:
            # beat = každých 100 px
            beat_width = 100

            for x in range(0, self.width, beat_width):
                pygame.draw.line(self.surface, self.beat_color, (x, 0), (x, self.height))

            # takt = každé 4 beaty
            bar_width = beat_width * self.beats_per_bar

            for x in range(0, self.width, bar_width):
                pygame.draw.line(self.surface, self.grid_color, (x, 0), (x, self.height))

        except Exception as e:
            Logger.error(f"TimelineRenderer grid error: {e}")

    # ---------------------------------------------------------
    # RENDER PLAYHEAD
    # ---------------------------------------------------------
    def _render_playhead(self) -> None:
        """Vykreslí playhead (render playhead)."""
        try:
            pygame.draw.line(
                self.surface,
                self.playhead_color,
                (self.playhead_x, 0),
                (self.playhead_x, self.height),
                2
            )
        except Exception as e:
            Logger.error(f"TimelineRenderer playhead error: {e}")

    # ---------------------------------------------------------
    # MAIN RENDER
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """
        Vykreslí celú časovú os a vráti surface (render timeline).
        """
        try:
            self.surface.fill(self.bg_color)
            self._render_grid()
            self._render_playhead()
            return self.surface

        except Exception as e:
            Logger.error(f"TimelineRenderer render error: {e}")
            return None
