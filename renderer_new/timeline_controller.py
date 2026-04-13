import pygame
from typing import Optional
from ..core.logger import Logger

from .timeline_grid import TimelineGrid
from .playhead import Playhead
from .timeline_layout_engine import TimelineLayoutEngine


class TimelineController:
    """
    TimelineController (Riadiaca jednotka časovej osi)
    --------------------------------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Spája TimelineGrid, Playhead a TimelineLayoutEngine
        - Poskytuje jednoduché API pre update() a render()
        - Slúži ako jediný vstupný bod pre Timeline v projekte
        - Pripravené pre integráciu s GraphicNotationRenderer a PlaybackEngine

    Vlastnosti:
        - Real‑time safe
        - Žiadne blokujúce operácie
        - Čistá architektúra
    """

    def __init__(
        self,
        width: int,
        height: int = 120,
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        self.width = width
        self.height = height

        # Layout engine (zoom, offset, pixel mapping)
        self.layout = TimelineLayoutEngine(
            pixels_per_beat=pixels_per_beat,
            beats_per_bar=beats_per_bar
        )

        # Grid (taktová a beatová mriežka)
        self.grid = TimelineGrid(
            width=width,
            height=height,
            beats_per_bar=beats_per_bar,
            pixels_per_beat=pixels_per_beat
        )

        # Playhead (prehrávacia hlava)
        self.playhead = Playhead(
            height=height,
            bpm=bpm,
            beats_per_bar=beats_per_bar,
            pixels_per_beat=pixels_per_beat
        )

        # Surface pre timeline
        self.surface = pygame.Surface((self.width, self.height))

        Logger.info("TimelineController initialized.")

    # ---------------------------------------------------------
    # EXTERNAL LAYOUT UPDATES (PixelLayoutEngine)
    # ---------------------------------------------------------
    def set_bounds(self, width: int, height: int) -> None:
        """Externé nastavenie veľkosti timeline (PixelLayoutEngine)."""
        try:
            self.width = max(1, int(width))
            self.height = max(1, int(height))

            self.surface = pygame.Surface((self.width, self.height))

            # Aktualizovať grid + playhead výšku
            self.grid.set_size(self.width, self.height)
            self.playhead.set_height(self.height)

        except Exception as e:
            Logger.error(f"TimelineController set_bounds error: {e}")

    # ---------------------------------------------------------
    # UPDATE TIMELINE STATE
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """
        Aktualizuje stav timeline (playhead, layout, atď.)
        """
        try:
            # Playhead update
            self.playhead.update(time_seconds)

            # Grid musí poznať zoom a offset
            self.grid.set_zoom(self.layout.zoom)
            self.grid.set_offset(self.layout.offset_x)

            # Playhead musí poznať zoom (pixels_per_beat)
            self.playhead.set_pixels_per_beat(self.layout.pixels_per_beat)

        except Exception as e:
            Logger.error(f"TimelineController update error: {e}")

    # ---------------------------------------------------------
    # RENDER TIMELINE
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """
        Vykreslí timeline a vráti surface (render timeline).
        """
        try:
            self.surface.fill((25, 25, 25))  # pozadie timeline

            # 1. Grid
            self.grid.render(self.surface)

            # 2. Playhead
            self.playhead.render(self.surface)

            return self.surface

        except Exception as e:
            Logger.error(f"TimelineController render error: {e}")
            return None

    # ---------------------------------------------------------
    # EXTERNAL CONTROLS
    # ---------------------------------------------------------
    def set_zoom(self, zoom: float) -> None:
        """Externé nastavenie zoomu timeline."""
        try:
            self.layout.set_zoom(zoom)
        except Exception:
            Logger.error("TimelineController set_zoom error.")

    def set_offset(self, offset_x: int) -> None:
        """Externé nastavenie posunu timeline."""
        try:
            self.layout.set_offset(offset_x)
        except Exception:
            Logger.error("TimelineController set_offset error.")
