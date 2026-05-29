# =========================================================
# TimelineRenderer v4.3.0
# Optimalizovaný fallback renderer pre timeline
# - real‑time safe
# - partial redraw friendly
# - diagnostické fallbacky
# =========================================================

import pygame
from typing import Tuple, Optional
from ..core.logger import Logger
from .timeline_controller import TimelineController


class TimelineRenderer:
    """
    TimelineRenderer (v4.3.0)
    -------------------------
    Účel:
        - Fallback renderer pre timeline (mimo LayerManager)
        - Deleguje kreslenie na TimelineController
        - Používa sa v TimelineUI alebo pri testovaní
        - Pripravené pre PixelLayoutEngine (v4)

    Vylepšenia v4.3.0:
        - bezpečnejšie fallbacky
        - optimalizované volania
        - partial redraw kompatibilné
        - real‑time safe
    """

    __slots__ = (
        "width", "height",
        "bg_color",
        "controller",
        "surface",
        "zoom",
        "scroll_x",
    )

    def __init__(
        self,
        width: int,
        height: int = 120,
        bg_color: Tuple[int, int, int] = (25, 25, 25),
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        # Dimensions
        try:
            self.width = max(1, int(width))
        except Exception:
            self.width = 1600

        try:
            self.height = max(1, int(height))
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
        if pygame is not None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                self.surface = None
        else:
            self.surface = None

        # View parameters
        self.zoom = 1.0
        self.scroll_x = 0.0

        Logger.info("TimelineRenderer initialized (v4.3.0).")

    # ---------------------------------------------------------
    # EXTERNAL LAYOUT (PixelLayoutEngine)
    # ---------------------------------------------------------
    def set_bounds(self, width: int, height: int) -> None:
        """Externé nastavenie veľkosti timeline."""
        if pygame is None:
            return

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
            z = max(0.1, min(float(zoom), 8.0))
            self.zoom = z
            if self.controller:
                self.controller.set_zoom(z)
        except Exception:
            Logger.error("TimelineRenderer set_zoom error.")

    def set_scroll(self, scroll_x: float) -> None:
        """Externé nastavenie horizontálneho posunu timeline."""
        try:
            sx = max(0.0, float(scroll_x))
            self.scroll_x = sx
            if self.controller:
                self.controller.set_scroll(sx)
        except Exception:
            Logger.error("TimelineRenderer set_scroll error.")

    # ---------------------------------------------------------
    # UPDATE PLAYBACK TIME
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """Aktualizuje timeline podľa času prehrávania."""
        ctrl = self.controller
        if ctrl is None:
            return

        try:
            ctrl.update(time_seconds)
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
        surf = self.surface
        ctrl = self.controller

        if surf is None or ctrl is None:
            return None

        try:
            surf.fill(self.bg_color)

            timeline_surface = ctrl.render()
            if timeline_surface is not None:
                surf.blit(timeline_surface, (0, 0))

            return surf

        except Exception as e:
            Logger.error(f"TimelineRenderer render error: {e}")
            return None
