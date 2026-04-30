import os
import pygame

from core.logger import Logger
from core.event_bus import EventBus
from core.event_types import MIDI_EXPORTED, ERROR_OCCURRED
from core.track_manager import TrackManager
from core.notation_processor import NotationProcessor
from core.playback_engine import PlaybackEngine

from ui.ui_manager import UIManager  # predpoklad: nový UI wrapper


def main():
    Logger.info("=== REAL-TIME MIDI NOTATION START (v2.0.0) ===")

    # Vycentrovanie okna
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    pygame.init()

    # Dynamické rozlíšenie
    info = pygame.display.Info()
    screen_width = min(info.current_w - 100, 1600)
    screen_height = min(info.current_h - 100, 900)

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        pygame.DOUBLEBUF | pygame.HWSURFACE,
    )
    pygame.display.set_caption("SIRIUS MIDI Engine | v2.0.0")

    clock = pygame.time.Clock()

    # EventBus
    event_bus = EventBus()

    # TrackManager + NotationProcessor + PlaybackEngine
    track_manager = TrackManager(track_system=None)  # ak máš TrackSystem, doplň ho sem
    notation_processor = NotationProcessor(track_system=None, event_bus=event_bus)
    playback_engine = PlaybackEngine(
        track_manager=track_manager,
        renderer=None,      # sem pôjde tvoj GraphicNotationRenderer / nový renderer
        canvas_ui=None,     # sem pôjde CanvasUI / UI časť, ktorá má playhead
        bpm=120.0,
        beats_per_bar=4,
    )

    # UI Manager (predpoklad: vie renderovať a má referenciu na playback/track manager)
    ui = UIManager(
        event_bus=event_bus,
        track_manager=track_manager,
        playback_engine=playback_engine,
    )

    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if playback_engine.is_playing():
                        playback_engine.pause()
                        Logger.info("Playback paused.")
                    else:
                        playback_engine.play()
                        Logger.info("Playback started.")

        # update času + rendereru
        surface = playback_engine.update()

        # UI render (predpoklad: UIManager.render(screen, dt, surface))
        ui.render(screen, dt, surface)

        pygame.display.flip()

    Logger.info("=== REAL-TIME MIDI NOTATION END ===")
    pygame.quit()


if __name__ == "__main__":
    main()
