# =========================================================
# TimelineController v4.3.0
# Optimalizovaný riadiaci modul pre timeline (grid, playhead, layout)
# - mikrooptimalizácie
# - bezpečné vykresľovanie
# - real-time safe
# - pripravené na diagnostiku a profiler
# =========================================================

from typing import Optional, List, Dict, Any

try:
    import pygame
except Exception:
    pygame = None

from ..core.logger import Logger
from .timeline_grid import TimelineGrid
from .playhead import Playhead
from .timeline_layout_engine import TimelineLayoutEngine


class TimelineController:
    """
    TimelineController (v4.3.0)
    ---------------------------
    Účel:
        - Riadi timeline (grid, playhead, layout)
        - Poskytuje API pre zoom, scroll, update, markers
        - Slúži ako zdroj pre TimelineLayer
        - Real‑time safe, bez blokujúcich operácií

    Vylepšenia v4.3.0:
        - bezpečnejšie fallbacky
        - stabilnejšia synchronizácia layout/grid/playhead
        - pripravené na diagnostiku a profiler
    """

    __slots__ = (
        "width",
        "height",
        "layout",
        "grid",
        "playhead",
        "markers",
        "surface",
        "font",
    )

    def __init__(
        self,
        width: int,
        height: int = 120,
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        # -----------------------------------------------------
        # SAFE INIT
        # -----------------------------------------------------
        try:
            self.width = max(1, int(width))
        except Exception:
            self.width = 1600

        try:
            self.height = max(1, int(height))
        except Exception:
            self.height = 120

        # -----------------------------------------------------
        # LAYOUT ENGINE (zoom, offset, pixel mapping)
        # -----------------------------------------------------
        self.layout = TimelineLayoutEngine(
            pixels_per_beat=pixels_per_beat,
            beats_per_bar=beats_per_bar
        )

        # -----------------------------------------------------
        # GRID (taktová a beatová mriežka)
        # -----------------------------------------------------
        self.grid = TimelineGrid(
            width=self.width,
            height=self.height,
            beats_per_bar=beats_per_bar,
            pixels_per_beat=pixels_per_beat
        )

        # -----------------------------------------------------
        # PLAYHEAD
        # -----------------------------------------------------
        self.playhead = Playhead(
            height=self.height,
            bpm=bpm,
            beats_per_bar=beats_per_bar,
            pixels_per_beat=pixels_per_beat
        )

        # -----------------------------------------------------
        # MARKERS
        # -----------------------------------------------------
        self.markers: List[Dict[str, Any]] = []

        # -----------------------------------------------------
        # SURFACE
        # -----------------------------------------------------
        if pygame is not None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                self.surface = None
        else:
            self.surface = None

        # -----------------------------------------------------
        # FONT
        # -----------------------------------------------------
        if pygame is not None:
            try:
                self.font = pygame.font.SysFont("Arial", 14)
            except Exception:
                self.font = None
        else:
            self.font = None

        Logger.info("TimelineController initialized (v4.3.0).")

    # ---------------------------------------------------------
    # EXTERNAL LAYOUT UPDATES
    # ---------------------------------------------------------
    def set_bounds(self, width: int, height: int) -> None:
        """Externé nastavenie veľkosti timeline."""
        if pygame is None:
            return

        try:
            self.width = max(1, int(width))
            self.height = max(1, int(height))

            self.surface = pygame.Surface((self.width, self.height))

            self.grid.set_size(self.width, self.height)
            self.playhead.set_height(self.height)

        except Exception as e:
            Logger.error(f"TimelineController set_bounds error: {e}")

    # ---------------------------------------------------------
    # ZOOM + SCROLL
    # ---------------------------------------------------------
    def set_zoom(self, zoom: float) -> None:
        """Externé nastavenie zoomu timeline."""
        try:
            self.layout.set_zoom(zoom)

            # Sync pixels_per_beat
            ppb = self.layout.pixels_per_beat
            self.grid.set_pixels_per_beat(ppb)
            self.playhead.set_pixels_per_beat(ppb)

        except Exception:
            Logger.error("TimelineController set_zoom error.")

    def set_scroll(self, offset_x: float) -> None:
        """Externé nastavenie posunu timeline."""
        try:
            self.layout.set_offset(offset_x)
            self.grid.set_offset(self.layout.offset_x)
        except Exception:
            Logger.error("TimelineController set_scroll error.")

    # ---------------------------------------------------------
    # MARKERS
    # ---------------------------------------------------------
    def set_markers(self, markers: List[Dict[str, Any]]) -> None:
        """Prijme markery z TimelineUI alebo rendereru."""
        if not isinstance(markers, (list, tuple)):
            return

        try:
            self.markers = list(markers)
        except Exception:
            # radšej necháme pôvodné markery, ako by sme mali zhodiť timeline
            pass

    # ---------------------------------------------------------
    # UPDATE TIMELINE STATE
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """Aktualizuje stav timeline (playhead, layout, grid)."""
        try:
            self.playhead.update(time_seconds)

            # Sync grid
            self.grid.set_zoom(self.layout.zoom)
            self.grid.set_offset(self.layout.offset_x)

            # Sync playhead
            self.playhead.set_pixels_per_beat(self.layout.pixels_per_beat)

        except Exception as e:
            Logger.error(f"TimelineController update error: {e}")

    # ---------------------------------------------------------
    # DRAW HELPERS (pre TimelineLayer)
    # ---------------------------------------------------------
    def draw_grid(self, surface) -> None:
        if surface is None:
            return
        try:
            self.grid.render(surface)
        except Exception:
            pass

    def draw_playhead(self, surface) -> None:
        if surface is None:
            return
        try:
            self.playhead.render(surface)
        except Exception:
            pass

    def draw_markers(self, surface) -> None:
        if pygame is None or surface is None:
            return

        for m in self.markers:
            if not isinstance(m, dict):
                continue

            t = m.get("time", m.get("timestamp"))
            if t is None:
                continue

            try:
                x = self.layout.time_to_x(t)
            except Exception:
                continue

            if not (0 <= x <= self.width):
                continue

            # Marker line
            try:
                pygame.draw.line(
                    surface,
                    (255, 200, 0),
                    (int(x), 0),
                    (int(x), self.height),
                    2
                )
            except Exception:
                pass

            # Marker name
            name = m.get("name", "")
            if self.font and name:
                try:
                    txt = self.font.render(name, True, (255, 200, 0))
                    surface.blit(txt, (int(x) + 4, 4))
                except Exception:
                    pass

    # ---------------------------------------------------------
    # MAIN RENDER ENTRY (fallback)
    # ---------------------------------------------------------
    def render(self) -> Optional["pygame.Surface"]:
        """
        Fallback render – používa sa len ak TimelineLayer nie je aktívna.
        V LayerManager architektúre sa používa TimelineLayer.draw().
        """
        if pygame is None or self.surface is None:
            return None

        try:
            self.surface.fill((25, 25, 25))

            self.draw_grid(self.surface)
            self.draw_markers(self.surface)
            self.draw_playhead(self.surface)

            return self.surface

        except Exception as e:
            Logger.error(f"TimelineController render error: {e}")
            return None
