import pygame
from typing import Tuple, Optional
from ..core.logger import Logger

from .timeline_controller import TimelineController


class TimelineRenderer:
    """
    TimelineRenderer (Časová os)
    ----------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Vykresľuje časovú os projektu
        - Deleguje grid + playhead na TimelineController
        - Slúži ako vizuálna vrstva pre TimelineUI
        - Pripravené pre PixelLayoutEngine

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
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        self.width = width
        self.height = height
        self.bg_color = bg_color

        # TimelineController = hlavná logika timeline
        self.controller = TimelineController(
            width=width,
            height=height,
            bpm=bpm,
            beats_per_bar=beats_per_bar,
            pixels_per_beat=pixels_per_beat
        )

        # Surface pre timeline
        self.surface = pygame.Surface((self.width, self.height))

        # Zoom + scroll (externé ovládanie)
        self.zoom = 1.0
        self.scroll_x = 0.0

        Logger.info("TimelineRenderer initialized.")

    # ---------------------------------------------------------
    # EXTERNAL LAYOUT (PixelLayoutEngine)
    # ---------------------------------------------------------
    def set_bounds(self, width: int, height: int) -> None:
        """Externé nastavenie veľkosti timeline (PixelLayoutEngine)."""
        try:
            self.width = max(1, int(width))
            self.height = max(1, int(height))

            self.surface = pygame.Surface((self.width, self.height))
            self.controller.set_bounds(self.width, self.height)

        except Exception as e:
            Logger.error(f"TimelineRenderer set_bounds error: {e}")

    # ---------------------------------------------------------
    # ZOOM + SCROLL
    # ---------------------------------------------------------
    def set_zoom(self, zoom: float) -> None:
        """Externé nastavenie zoomu timeline."""
        self.zoom = max(0.1, min(zoom, 8.0))
        self.controller.set_zoom(self.zoom)

    def set_scroll(self, scroll_x: float) -> None:
        """Externé nastavenie horizontálneho posunu timeline."""
        self.scroll_x = max(0.0, scroll_x)
        self.controller.set_scroll(self.scroll_x)

    # ---------------------------------------------------------
    # UPDATE PLAYBACK TIME
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """Aktualizuje timeline podľa času prehrávania."""
        try:
            self.controller.update(time_seconds)
        except Exception as e:
            Logger.error(f"TimelineRenderer update error: {e}")

    # ---------------------------------------------------------
    # MAIN RENDER
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """
        Vykreslí celú časovú os a vráti surface (render timeline).
        """
        try:
            self.surface.fill(self.bg_color)

            # TimelineController vykreslí grid + barlines + playhead
            timeline_surface = self.controller.render()
            if timeline_surface is not None:
                self.surface.blit(timeline_surface, (0, 0))

            return self.surface

        except Exception as e:
            Logger.error(f"TimelineRenderer render error: {e}")
            return None
