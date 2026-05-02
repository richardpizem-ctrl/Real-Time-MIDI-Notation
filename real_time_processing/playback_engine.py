# =========================================================
# PlaybackEngine v2.0.0
# Stabilný real‑time prehrávací motor pre Timeline Renderer
# =========================================================

import time
import pygame
from typing import Optional
from ..core.logger import Logger
from ..renderer_new.timeline_controller import TimelineController


class PlaybackEngine:
    """
    PlaybackEngine (v2.0.0)
    -----------------------
    Účel:
        - Riadi čas prehrávania (time_seconds)
        - Volá update() a render() pre timeline
        - Slúži ako centrálny prehrávací motor pre notáciu
        - Pripravené pre budúcu integráciu s audio/MIDI playback (v3)

    Vlastnosti:
        - Real‑time safe
        - Stabilné časovanie
        - Jednoduché API: play(), stop(), update(), render()
    """

    def __init__(
        self,
        width: int = 1600,
        timeline_height: int = 120,
        bpm: float = 120.0
    ) -> None:

        try:
            self.width = int(width)
        except Exception:
            self.width = 1600

        try:
            self.timeline_height = int(timeline_height)
        except Exception:
            self.timeline_height = 120

        try:
            self.bpm = float(bpm)
        except Exception:
            self.bpm = 120.0

        # Playback state
        self.is_playing: bool = False
        self.start_time: float = 0.0
        self.time_seconds: float = 0.0

        # Timeline controller
        try:
            self.timeline = TimelineController(
                width=self.width,
                height=self.timeline_height,
                bpm=self.bpm
            )
        except Exception as e:
            Logger.error(f"PlaybackEngine init TimelineController error: {e}")
            raise

        # Surface pre timeline
        try:
            self.surface = pygame.Surface((self.width, self.timeline_height))
        except Exception:
            self.surface = None
            Logger.error("PlaybackEngine: Failed to create pygame Surface.")

        Logger.info("PlaybackEngine initialized (v2.0.0).")

    # ---------------------------------------------------------
    # PLAYBACK CONTROL
    # ---------------------------------------------------------
    def play(self) -> None:
        """Spustí prehrávanie."""
        try:
            self.is_playing = True
            self.start_time = time.perf_counter()
            Logger.info("Playback started.")
        except Exception as e:
            Logger.error(f"PlaybackEngine play error: {e}")

    def stop(self) -> None:
        """Zastaví prehrávanie."""
        try:
            self.is_playing = False
            self.time_seconds = 0.0
            Logger.info("Playback stopped.")
        except Exception as e:
            Logger.error(f"PlaybackEngine stop error: {e}")

    # ---------------------------------------------------------
    # UPDATE LOOP
    # ---------------------------------------------------------
    def update(self) -> None:
        """
        Aktualizuje čas a timeline.
        Volá sa každý frame.
        """
        try:
            if self.is_playing:
                self.time_seconds = time.perf_counter() - self.start_time

            self.timeline.update(self.time_seconds)

        except Exception as e:
            Logger.error(f"PlaybackEngine update error: {e}")

    # ---------------------------------------------------------
    # RENDER LOOP
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """
        Vykreslí timeline a vráti surface.
        """
        if self.surface is None:
            Logger.error("PlaybackEngine render error: surface is None.")
            return None

        try:
            self.surface.fill((20, 20, 20))

            timeline_surface = self.timeline.render()
            if timeline_surface is not None:
                self.surface.blit(timeline_surface, (0, 0))

            return self.surface

        except Exception as e:
            Logger.error(f"PlaybackEngine render error: {e}")
            return None
