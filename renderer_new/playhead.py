# =========================================================
# Playhead v2.0.0
# Stabilná real‑time prehrávacia hlava pre Timeline Renderer
# =========================================================

import pygame
from typing import Tuple
from ..core.logger import Logger


class Playhead:
    """
    Playhead (v2.0.0)
    -----------------
    Účel:
        - Vertikálna čiara ukazujúca aktuálnu pozíciu prehrávania
        - Používa sa v timeline aj v grafickej notácii
        - Oddelená logika výpočtu pozície a vykreslenia

    Vlastnosti:
        - Real‑time safe
        - Žiadne blokujúce operácie
        - Glow cache pre výkon
        - Pripravené pre PixelLayoutEngine (v3)
    """

    def __init__(
        self,
        height: int,
        color: Tuple[int, int, int] = (255, 80, 80),
        bpm: float = 120.0,
        beats_per_bar: int = 4,
        pixels_per_beat: int = 100
    ) -> None:

        try:
            self.height = max(1, int(height))
        except Exception:
            self.height = 100

        self.color = color

        try:
            self.bpm = max(1.0, float(bpm))
        except Exception:
            self.bpm = 120.0

        try:
            self.beats_per_bar = max(1, int(beats_per_bar))
        except Exception:
            self.beats_per_bar = 4

        try:
            self.pixels_per_beat = max(1, int(pixels_per_beat))
        except Exception:
            self.pixels_per_beat = 100

        # Zoom + offset
        self.zoom = 1.0
        self.offset_x = 0

        # Aktuálna pozícia playheadu v pixeloch
        self.x = 0

        # Glow cache
        self._glow_surface: pygame.Surface | None = None
        self._rebuild_glow_surface()

        Logger.info("Playhead initialized (v2.0.0).")

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
        """
        Vykreslí playhead na daný surface.
        """
        if surface is None:
            return

        try:
            # Glow efekt
            if self._glow_surface is not None:
                surface.blit(self._glow_surface, (self.x - 3, 0))

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
