# =========================================================
# Playhead v4.3.0
# Optimalizovaná real‑time prehrávacia hlava pre Timeline Renderer
# - mikrooptimalizácie
# - glow cache optimalizácia
# - diagnostika (RenderProfiler hook-ready)
# - real‑time safe
# - partial redraw friendly
# =========================================================

import pygame
from typing import Tuple, Optional
from ..core.logger import Logger


class Playhead:
    """
    Playhead (v4.3.0)
    -----------------
    Účel:
        - Vertikálna čiara ukazujúca aktuálnu pozíciu prehrávania
        - Používa sa v timeline aj v grafickej notácii
        - Oddelená logika výpočtu pozície a vykreslenia

    Vylepšenia v4.3.0:
        - optimalizované výpočty
        - bezpečné fallbacky
        - glow cache optimalizácia
        - pripravené pre RenderProfiler
        - real‑time safe
        - partial redraw kompatibilné
    """

    __slots__ = (
        "height", "color", "bpm", "beats_per_bar", "pixels_per_beat",
        "zoom", "offset_x", "x", "_glow_surface"
    )

    def __init__(
        self,
        height: int,
        color: Tuple[int, int, int] = (255, 80, 80),
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        # Height
        try:
            self.height = max(1, int(height))
        except Exception:
            self.height = 100

        self.color = color

        # BPM
        try:
            self.bpm = max(1.0, float(bpm))
        except Exception:
            self.bpm = 120.0

        # Beats per bar
        try:
            self.beats_per_bar = max(1, int(beats_per_bar))
        except Exception:
            self.beats_per_bar = 4

        # Pixels per beat
        try:
            self.pixels_per_beat = max(1, int(pixels_per_beat))
        except Exception:
            self.pixels_per_beat = 100

        # View parameters
        self.zoom = 1.0
        self.offset_x = 0
        self.x = 0

        # Glow cache
        self._glow_surface: Optional[pygame.Surface] = None
        self._rebuild_glow_surface()

        Logger.info("Playhead initialized (v4.3.0).")

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _rebuild_glow_surface(self) -> None:
        """Vytvorí alebo obnoví glow surface podľa aktuálnej výšky a farby."""
        try:
            surf = pygame.Surface((6, self.height), pygame.SRCALPHA)
            pygame.draw.rect(
                surf,
                (*self.color, 70),
                surf.get_rect(),
                border_radius=3
            )
            self._glow_surface = surf
        except Exception:
            self._glow_surface = None
            Logger.error("Playhead _rebuild_glow_surface error.")

    # ---------------------------------------------------------
    # SETTERS
    # ---------------------------------------------------------
    def set_height(self, height: int) -> None:
        try:
            self.height = max(1, int(height))
            self._rebuild_glow_surface()
        except Exception:
            Logger.error("Playhead set_height error.")

    def set_bpm(self, bpm: float) -> None:
        try:
            self.bpm = max(1.0, float(bpm))
        except Exception:
            Logger.error("Playhead set_bpm error.")

    def set_pixels_per_beat(self, ppb: int) -> None:
        try:
            self.pixels_per_beat = max(1, int(ppb))
        except Exception:
            Logger.error("Playhead set_pixels_per_beat error.")

    def set_zoom(self, zoom: float) -> None:
        """Externé nastavenie zoomu (od TimelineController)."""
        try:
            self.zoom = max(0.1, float(zoom))
        except Exception:
            Logger.error("Playhead set_zoom error.")

    def set_offset(self, offset_x: int) -> None:
        """Externé nastavenie scroll offsetu."""
        try:
            self.offset_x = int(offset_x)
        except Exception:
            Logger.error("Playhead set_offset error.")

    # ---------------------------------------------------------
    # UPDATE POSITION
    # ---------------------------------------------------------
    def update(self, time_seconds: float) -> None:
        """
        Aktualizuje pozíciu playheadu podľa času.
        Real‑time safe.
        """
        try:
            if time_seconds is None or time_seconds < 0:
                return

            beats_per_second = self.bpm / 60.0
            total_beats = time_seconds * beats_per_second

            zoomed_ppb = self.pixels_per_beat * self.zoom
            raw_x = total_beats * zoomed_ppb

            self.x = int(raw_x - self.offset_x)

        except Exception as e:
            Logger.error(f"Playhead update error: {e}")

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        """Vykreslí playhead na daný surface."""
        if surface is None:
            return

        try:
            # Glow efekt
            glow = self._glow_surface
            if glow is not None:
                surface.blit(glow, (self.x - 3, 0))

            # Hlavná čiara
            pygame.draw.line(
                surface,
                self.color,
                (self.x, 0),
                (self.x, self.height),
                2
            )

        except Exception as e:
            Logger.error(f"Playhead render error: {e}")
