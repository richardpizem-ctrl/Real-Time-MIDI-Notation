import time
import pygame
from typing import Optional
from ..core.logger import Logger
from ..renderer_new.timeline_controller import TimelineController


class PlaybackEngine:
    """
    PlaybackEngine (Prehrávací motor)
    ---------------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Riadi čas prehrávania (time_seconds)
        - Volá update() a render() pre timeline
        - Slúži ako centrálny motor pre prehrávanie MIDI/notation
        - Pripravené pre budúcu integráciu s audio/MIDI playback

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

        self.width = width
        self.timeline_height = timeline_height
        self.bpm = bpm

        # Playback state
        self.is_playing = False
        self.start_time: float = 0.0
        self.time_seconds: float = 0.0

        # Timeline controller
        self.timeline = TimelineController(
            width=self.width,
            height=self.timeline_height,
            bpm=self.bpm
        )

        # Surface pre timeline
        self.surface = pygame.Surface((self.width, self.timeline_height))

        Logger.info("PlaybackEngine initialized.")

    # ---------------------------------------------------------
    # PLAYBACK CONTROL
    # ---------------------------------------------------------
    def play(self) -> None:
        """Spustí prehrávanie."""
        try:
            self.is_playing = True
            self.start_time = time.time()
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
                self.time_seconds = time.time() - self.start_time

            # Update timeline
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
        try:
            self.surface.fill((20, 20, 20))
            timeline_surface = self.timeline.render()

            if timeline_surface:
                self.surface.blit(timeline_surface, (0, 0))

            return self.surface

        except Exception as e:
            Logger.error(f"PlaybackEngine render error: {e}")
            return None
