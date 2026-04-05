# run.py – hlavný spúšťací súbor pre Real-Time MIDI Notation

import pygame

from event_bus.event_bus import EventBus
from event_bus.event_types import (
    NOTE_RECORDED,
    TRACK_SELECTED,
    MIDI_EXPORTED,
    ERROR_OCCURRED
)

from track_system.track_system import TrackSystem
from notation_processor.notation_processor import NotationProcessor

from ui.ui_manager import UIManager
from real_time_processing.stream_handler import StreamHandler
from midi_input.event_router import EventRouter

from core.logger import Logger

# NOVÉ IMPORTY
from core.track_manager import TrackManager
from renderer.graphic_renderer import GraphicNotationRenderer
from ui.canvas_ui import CanvasUI
from core.playback_engine import PlaybackEngine


# ---------------------------------------------------------
# TEST HANDLERY
# ---------------------------------------------------------
def on_note_recorded(data):
    Logger.info(f"[TEST] NOTE_RECORDED event received: {data}")

def on_track_selected(data):
    Logger.info(f"[TEST] TRACK_SELECTED event received: {data}")

def on_midi_exported(data):
    Logger.info(f"[TEST] MIDI_EXPORTED event received: {data}")

def on_error(data):
    Logger.error(f"[TEST] ERROR_OCCURRED: {data}")


# ---------------------------------------------------------
# HLAVNÁ FUNKCIA
# ---------------------------------------------------------
def main():
    Logger.info("=== REAL-TIME MIDI NOTATION START ===")

    # -----------------------------------------------------
    # 0. Inicializácia pygame
    # -----------------------------------------------------
    try:
        pygame.init()
        screen = pygame.display.set_mode((1400, 1100))
        clock = pygame.time.Clock()
    except Exception as e:
        Logger.error(f"Pygame initialization error: {e}")
        return

    # -----------------------------------------------------
    # 1. EventBus
    # -----------------------------------------------------
    event_bus = EventBus()

    try:
        event_bus.subscribe(NOTE_RECORDED, on_note_recorded)
        event_bus.subscribe(TRACK_SELECTED, on_track_selected)
        event_bus.subscribe(MIDI_EXPORTED, on_midi_exported)
        event_bus.subscribe(ERROR_OCCURRED, on_error)
    except Exception as e:
        Logger.error(f"Failed to subscribe handlers: {e}")

    # -----------------------------------------------------
    # 2. TrackSystem + NotationProcessor
    # -----------------------------------------------------
    try:
        track_system = TrackSystem(event_bus)
        notation_processor = NotationProcessor(track_system, event_bus)
    except Exception as e:
        Logger.error(f"Failed to initialize TrackSystem or NotationProcessor: {e}")
        return

    # -----------------------------------------------------
    # 3. UI Manager
    # -----------------------------------------------------
    try:
        ui = UIManager(
            width=1400,
            height=1100,
            track_system=track_system,
            notation_processor=notation_processor,
        )
    except Exception as e:
        Logger.error(f"Failed to initialize UIManager: {e}")
        return

    try:
        notation_processor.bind_staff(ui.staff)
        notation_processor.bind_piano(ui.piano)
        notation_processor.bind_visualizer(ui.visualizer)
    except Exception as e:
        Logger.error(f"Failed to bind UI components to NotationProcessor: {e}")

    # -----------------------------------------------------
    # 4. EventRouter (MIDI → EventBus → UI)
    # -----------------------------------------------------
    try:
        event_router = EventRouter(
            event_bus=event_bus,
            ui_manager=ui
        )
    except Exception as e:
        Logger.error(f"Failed to initialize EventRouter: {e}")
        return

    # -----------------------------------------------------
    # 5. MIDI Stream Handler
    # -----------------------------------------------------
    try:
        stream_handler = StreamHandler(
            ui_manager=ui,
            event_router=event_router
        )
    except Exception as e:
        Logger.error(f"Failed to initialize StreamHandler: {e}")
        return

    # -----------------------------------------------------
    # 6. NOVÉ: TrackManager + Renderer + CanvasUI + PlaybackEngine
    # -----------------------------------------------------
    try:
        track_manager = TrackManager(track_system)

        canvas_ui = CanvasUI(parent=None)  # CanvasUI beží mimo pygame okna
        renderer = GraphicNotationRenderer(
            width=1400,
            height=400,
            track_manager=track_manager
        )

        playback = PlaybackEngine(
            track_manager=track_manager,
            renderer=renderer,
            canvas_ui=canvas_ui,
            bpm=120.0,
            beats_per_bar=4
        )

        # DEMO: prázdne noty (môžeš neskôr nahradiť MIDI loaderom)
        playback.set_notes([])
    except Exception as e:
        Logger.error(f"Failed to initialize PlaybackEngine stack: {e}")
        return

    # -----------------------------------------------------
    # 7. HLAVNÁ RENDER SLUČKA
    # -----------------------------------------------------
    running = True
    while running:
        try:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                ui.handle_event(event)

            # MIDI vstup
            stream_handler.poll()

            # Playback engine tick
            playback_surface = playback.update()

            # UI kreslenie
            ui.draw(screen)

            # Renderer kreslenie (ak existuje surface)
            if playback_surface is not None:
                screen.blit(playback_surface, (0, 700))

            pygame.display.update()
            clock.tick(60)

        except Exception as e:
            Logger.error(f"Main loop error: {e}")

    pygame.quit()
    Logger.info("=== END ===")


if __name__ == "__main__":
    main()
