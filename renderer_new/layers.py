import pygame
from typing import Optional, List, Dict, Any
from ..core.logger import Logger

from .timeline_grid import TimelineGrid
from .playhead import Playhead
from .timeline_layout_engine import TimelineLayoutEngine


class TimelineController:
    """
    TimelineController – FÁZA 4 (kompletná stabilizovaná verzia)

    Účel:
        - Riadi timeline (grid, playhead, layout)
        - Poskytuje API pre zoom, scroll, update, markers
        - Slúži ako zdroj pre renderer_layers (GridLayer, MarkerLayer, PlayheadLayer)
        - Real‑time safe, bez blokujúcich operácií
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

        # Markery
        self.markers: List[Dict[str, Any]] = []

        # Surface pre timeline
        self.surface = pygame.Surface((self.width, self.height))

        # Font pre ruler / markers
        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None

        Logger.info("TimelineController initialized (FÁZA 4).")

    # ---------------------------------------------------------
    # EXTERNAL LAYOUT UPDATES
    # ---------------------------------------------------------
    def set_bounds(self, width: int, height: int) -> None:
        """Externé nastavenie veľkosti timeline."""
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

            # Grid + playhead musia poznať nové pixels_per_beat
            self.grid.set_pixels_per_beat(self.layout.pixels_per_beat)
            self.playhead.set_pixels_per_beat(self.layout.pixels_per_beat)

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
        if isinstance(markers, (list, tuple)):
            self.markers = list(markers)

    # ---------------------------------------------------------
    # UPDATE TIMELINE STATE
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """Aktualizuje stav timeline (playhead, layout, grid)."""
        try:
            self.playhead.update(time_seconds)

            # Grid sync
            self.grid.set_zoom(self.layout.zoom)
            self.grid.set_offset(self.layout.offset_x)

            # Playhead sync
            self.playhead.set_pixels_per_beat(self.layout.pixels_per_beat)

        except Exception as e:
            Logger.error(f"TimelineController update error: {e}")

    # ---------------------------------------------------------
    # DRAW HELPERS (pre LayerManager)
    # ---------------------------------------------------------
    def draw_grid(self, surface):
        """Kreslí beaty, takty, subdivízie."""
        try:
            self.grid.render(surface)
        except Exception:
            pass

    def draw_playhead(self, surface):
        """Kreslí playhead."""
        try:
            self.playhead.render(surface)
        except Exception:
            pass

    def draw_markers(self, surface):
        """Kreslí markery na timeline."""
        if pygame is None or surface is None:
            return

        for m in self.markers:
            if not isinstance(m, dict):
                continue

            t = m.get("time", m.get("timestamp"))
            if t is None:
                continue

            # prepočet času na X pozíciu cez layout engine
            try:
                x = self.layout.time_to_x(t)
            except Exception:
                continue

            if not (0 <= x <= self.width):
                continue

            # marker line
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

            # marker name
            name = m.get("name", "")
            if self.font and name:
                try:
                    txt = self.font.render(name, True, (255, 200, 0))
                    surface.blit(txt, (int(x) + 4, 4))
                except Exception:
                    pass

    # ---------------------------------------------------------
    # MAIN RENDER ENTRY
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """Vykreslí timeline a vráti surface."""
        try:
            self.surface.fill((25, 25, 25))

            # 1. Grid
            self.draw_grid(self.surface)

            # 2. Markers
            self.draw_markers(self.surface)

            # 3. Playhead
            self.draw_playhead(self.surface)

            return self.surface

        except Exception as e:
            Logger.error(f"TimelineController render error: {e}")
            return None
