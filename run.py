# =========================================================
# run.py – Real-Time MIDI Notation v2.0.0
# Stabilný hlavný spúšťací súbor
# =========================================================

import pygame
import os

# ---------------------------------------------------------
# CORE
# ---------------------------------------------------------
from core.logger import Logger
from core.event_bus import EventBus
from core.event_types import ERROR_OCCURRED
from core.track_manager import TrackManager
from core.notation_processor import NotationProcessor
from core.playback_engine import PlaybackEngine

# ---------------------------------------------------------
# RENDERER + UI
# ---------------------------------------------------------
from renderer_new.graphic_renderer import GraphicNotationRenderer
from renderer_new.pixel_layout_engine import PixelLayoutEngine
from ui.timeline_ui import TimelineUI
from ui.canvas_ui import CanvasUI


# ---------------------------------------------------------
# MAIN FUNCTION
# ---------------------------------------------------------
def main():
    Logger.info("=== REAL-TIME MIDI NOTATION v2.0.0 START ===")

    # -----------------------------------------------------
    # 0. Pygame initialization
    # -----------------------------------------------------
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    try:
        pygame.init()
        pygame.display.set_caption("Real-Time MIDI Notation | v2.0.0")

        screen = pygame.display.set_mode(
            (1600, 1000),
            pygame.DOUBLEBUF | pygame.HWSURFACE
        )
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
    # 3. Renderer stack
    # -----------------------------------------------------
    try:
        layout_engine = PixelLayoutEngine()

        renderer = GraphicNotationRenderer(
            layout_engine=layout_engine,
            track_manager=track_manager,
            width=1600,
            height=300
        )
    except Exception as e:
        Logger.error(f"Failed to initialize renderer stack: {e}")
        return

    # -----------------------------------------------------
    # 4. UI (TimelineUI + CanvasUI)
    # -----------------------------------------------------
    try:
        timeline_ui = TimelineUI(
            track_manager=track_manager,
            notation_processor=notation_processor,
            width=1600,
            height=200
        )

        canvas_ui = CanvasUI(
            width=1600,
            height=500,
            renderer=renderer
        )
    except Exception as e:
        Logger.error(f"Failed to initialize UI: {e}")
        return

    # -----------------------------------------------------
    # 5. PlaybackEngine
    # -----------------------------------------------------
    try:
        playback = PlaybackEngine(
            track_manager=track_manager,
            renderer=renderer,
            canvas_ui=canvas_ui,
            bpm=120.0,
            beats_per_bar=4
        )
    except Exception as e:
        Logger.error(f"Failed to initialize PlaybackEngine: {e}")
        return

    # -----------------------------------------------------
    # 6. MAIN LOOP
    # -----------------------------------------------------
    running = True

    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # UI event handling
            timeline_ui.handle_event(event)
            canvas_ui.handle_event(event)

            # Playback toggle
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if playback.is_playing():
                        playback.pause()
                        Logger.info("Playback paused.")
                    else:
                        playback.play()
                        Logger.info("Playback started.")

        # Update
        playback_surface = playback.update(dt)

        # Render
        screen.fill((20, 20, 20))

        timeline_ui.render(screen)
        canvas_ui.render(screen, playback_surface)

        pygame.display.flip()

    pygame.quit()
    Logger.info("=== END ===")


if __name__ == "__main__":
    main()
