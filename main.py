# =========================================================
# main.py – Real-Time MIDI Notation v2.0.0
# Stabilný hlavný spúšťací súbor pre SIRIUS MIDI Engine
# =========================================================

import os
import pygame

from core.logger import Logger
from core.event_bus import EventBus
from core.event_types import MIDI_EXPORTED, ERROR_OCCURRED
from core.track_manager import TrackManager
from core.notation_processor import NotationProcessor
from core.playback_engine import PlaybackEngine

from ui.ui_manager import UIManager  # nový UI wrapper v2


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
def main():
    Logger.info("=== REAL-TIME MIDI NOTATION START (v2.0.0) ===")

    # -----------------------------------------------------
    # 0. Pygame initialization
    # -----------------------------------------------------
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    try:
        pygame.init()

        info = pygame.display.Info()
        screen_width = min(info.current_w - 100, 1600)
        screen_height = min(info.current_h - 100, 900)

        screen = pygame.display.set_mode(
            (screen_width, screen_height),
            pygame.DOUBLEBUF | pygame.HWSURFACE,
        )
        pygame.display.set_caption("SIRIUS MIDI Engine | v2.0.0")

        clock = pygame.time.Clock()

    except Exception as e:
        Logger.error(f"Pygame initialization error: {e}")
        return

    # -----------------------------------------------------
    # 1. EventBus
    # -----------------------------------------------------
    event_bus = EventBus()

    def on_error(msg):
        Logger.error(f"[ERROR] {msg}")

    event_bus.subscribe(ERROR_OCCURRED, on_error)

    # -----------------------------------------------------
    # 2. TrackManager + NotationProcessor
    # -----------------------------------------------------
    try:
        track_manager = TrackManager(event_bus=event_bus)
        notation_processor = NotationProcessor(
            track_manager=track_manager,
            event_bus=event_bus
        )
    except Exception as e:
        Logger.error(f"Failed to initialize TrackManager or NotationProcessor: {e}")
        return

    # -----------------------------------------------------
    # 3. PlaybackEngine
    # -----------------------------------------------------
    try:
        playback_engine = PlaybackEngine(
            track_manager=track_manager,
            renderer=None,      # renderer sa doplní v UIManager v2
            canvas_ui=None,     # UIManager v2 poskytuje CanvasUI
            bpm=120.0,
            beats_per_bar=4,
        )
    except Exception as e:
        Logger.error(f"Failed to initialize PlaybackEngine: {e}")
        return

    # -----------------------------------------------------
    # 4. UI Manager (v2.0.0)
    # -----------------------------------------------------
    try:
        ui = UIManager(
            event_bus=event_bus,
            track_manager=track_manager,
            playback_engine=playback_engine,
            screen_width=screen_width,
            screen_height=screen_height,
        )
    except Exception as e:
        Logger.error(f"Failed to initialize UIManager: {e}")
        return

    # -----------------------------------------------------
    # 5. MAIN LOOP
    # -----------------------------------------------------
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # UI event handling
            ui.handle_event(event)

            # Playback toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if playback_engine.is_playing():
                        playback_engine.pause()
                        Logger.info("Playback paused.")
                    else:
                        playback_engine.play()
                        Logger.info("Playback started.")

        # Update
        surface = playback_engine.update()

        # Render
        ui.render(screen, dt, surface)

        pygame.display.flip()

    Logger.info("=== REAL-TIME MIDI NOTATION END ===")
    pygame.quit()


if __name__ == "__main__":
    main()
