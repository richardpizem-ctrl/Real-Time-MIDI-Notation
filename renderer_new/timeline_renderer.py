# =========================================================
# TimelineRenderer v2.0.0
# Stabilný fallback renderer pre timeline (grid + markers + playhead)
# =========================================================

import pygame
from typing import Tuple, Optional
from ..core.logger import Logger
from .timeline_controller import TimelineController


class TimelineRenderer:
    """
    TimelineRenderer (v2.0.0)
    -------------------------
    Účel:
        - Fallback renderer pre timeline (mimo LayerManager)
        - Deleguje kreslenie na TimelineController
        - Používa sa v TimelineUI alebo pri testovaní
        - Pripravené pre PixelLayoutEngine (v3)

    Vlastnosti:
        - Real‑time safe
        - Žiadne blokujúce operácie
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

        try:
            self.width = int(width)
        except Exception:
            self.width = 1600

        try:
            self.height = int(height)
        except Exception:
            self.height = 120

        self.bg_color = bg_color

        # TimelineController = hlavná logika timeline
        try:
            self.controller = TimelineController(
                width=self.width,
                height=self.height,
                bpm=bpm,
                beats_per_bar=beats_per_bar,
                pixels_per_beat=pixels_per_beat
            )
        except Exception as e:
            Logger.error(f"TimelineRenderer init controller error: {e}")
            self.controller = None

        # Surface pre timeline
        try:
            self.surface = pygame.Surface((self.width, self.height))
        except Exception:
            self.surface = None

        # Zoom + scroll (externé ovládanie)
        self.zoom = 1.0
        self.scroll_x = 0.0

        Logger.info("TimelineRenderer initialized (v2.0.0).")

    # ---------------------------------------------------------
    # EXTERNAL LAYOUT (PixelLayoutEngine)
    # ---------------------------------------------------------
    def set_bounds(self, width: int, height: int) -> None:
        """Externé nastavenie veľkosti timeline."""
        try:
            self.width = max(1, int(width))
            self.height = max(1, int(height))

            self.surface = pygame.Surface((self.width, self.height))

            if self.controller:
                self.controller.set_bounds(self.width, self.height)

        except Exception as e:
            Logger.error(f"TimelineRenderer set_bounds error: {e}")

    # ---------------------------------------------------------
    # ZOOM + SCROLL
    # ---------------------------------------------------------
    def set_zoom(self, zoom: float) -> None:
        """Externé nastavenie zoomu timeline."""
        try:
            self.zoom = max(0.1, min(float(zoom), 8.0))
            if self.controller:
                self.controller.set_zoom(self.zoom)
        except Exception:
            Logger.error("TimelineRenderer set_zoom error.")

    def set_scroll(self, scroll_x: float) -> None:
        """Externé nastavenie horizontálneho posunu timeline."""
        try:
            self.scroll_x = max(0.0, float(scroll_x))
            if self.controller:
                self.controller.set_scroll(self.scroll_x)
        except Exception:
            Logger.error("TimelineRenderer set_scroll error.")

    # ---------------------------------------------------------
    # UPDATE PLAYBACK TIME
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """Aktualizuje timeline podľa času prehrávania."""
        if not self.controller:
            return

        try:
            self.controller.update(time_seconds)
        except Exception as e:
            Logger.error(f"TimelineRenderer update error: {e}")

    # ---------------------------------------------------------
    # MAIN RENDER
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """
        Vykreslí celú časovú os a vráti surface.
        Toto je fallback render – v LayerManager architektúre
        sa používa TimelineLayer.draw().
        """
        if self.surface is None or self.controller is None:
            return None

        try:
            self.surface.fill(self.bg_color)

            timeline_surface = self.controller.render()
            if timeline_surface is not None:
                self.surface.blit(timeline_surface, (0, 0))

            return self.surface

        except Exception as e:
            Logger.error(f"TimelineRenderer render error: {e}")
            return None
