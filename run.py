# run.py – hlavný spúšťací súbor pre Real-Time MIDI Notation

import pygame

# ---------------------------------------------------------
# EVENT BUS
# ---------------------------------------------------------
from event_bus.event_bus import EventBus
from event_bus.event_types import (
    NOTE_RECORDED,
    TRACK_SELECTED,
    MIDI_EXPORTED,
    ERROR_OCCURRED
)

# ---------------------------------------------------------
# CORE / TRACKS / PROCESSING
# ---------------------------------------------------------
from core.logger import Logger
    from core.track_manager import TrackManager
from core.playback_engine import PlaybackEngine

from track_system.track_system import TrackSystem
from notation_processor.notation_processor import NotationProcessor

# ---------------------------------------------------------
# UI
# ---------------------------------------------------------
from ui.ui_manager import UIManager
from ui.canvas_ui import CanvasUI

# ---------------------------------------------------------
# MIDI INPUT
# ---------------------------------------------------------
from midi_input.event_router import EventRouter
from real_time_processing.stream_handler import StreamHandler

# ---------------------------------------------------------
# RENDERER
# ---------------------------------------------------------
from renderer.graphic_renderer import GraphicNotationRenderer

# ---------------------------------------------------------
# AI MODULE
# ---------------------------------------------------------
from AI.ai_core import AIEngine
from AI.Kvantizér.smart_quantizer import SmartQuantizer
from AI.Interpretácia.performance_interpreter import PerformanceInterpreter
from AI.Notácia.notation_predictor import NotationPredictor


# ---------------------------------------------------------
# TEST HANDLERY (TEST ONLY)
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
        pygame.display.set_caption("Real-Time MIDI Notation")
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
    # 3. AI ENGINE (NOVÉ)
    # -----------------------------------------------------
    try:
        ai_engine = AIEngine(
            quantizer=SmartQuantizer(),
            interpreter=PerformanceInterpreter(),
            notation_engine=NotationPredictor()
        )

        # Prepojenie AI → NotationProcessor (bez zásahu do vnútra)
        notation_processor.attach_ai(ai_engine)

        Logger.info("AI Engine initialized and attached.")
    except Exception as e:
        Logger.error(f"Failed to initialize AI Engine: {e}")

    # -----------------------------------------------------
    # 4. UI Manager
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
    # 5. EventRouter (MIDI → EventBus → UI)
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
    # 6. MIDI Stream Handler
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
    # 7. TrackManager + Renderer + CanvasUI + PlaybackEngine
    # -----------------------------------------------------
    try:
        track_manager = TrackManager(track_system)

        canvas_ui = CanvasUI(parent=None)
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

        playback.set_notes([])  # TODO: Replace with MIDI loader
    except Exception as e:
        Logger.error(f"Failed to initialize PlaybackEngine stack: {e}")
        return

    # -----------------------------------------------------
    # 8. HLAVNÁ RENDER SLUČKA
    # -----------------------------------------------------
    running = True
    try:
        while running:
            dt = clock.tick(60) / 1000.0   # DELTA TIME FIX

            try:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    try:
                        ui.handle_event(event)
                    except Exception as e:
                        Logger.error(f"UI event error: {e}")

                # MIDI burst-safe polling
                stream_handler.poll(max_messages=64)

                # Delta-time aware playback
                playback_surface = playback.update(dt=dt)

                ui.draw(screen)

                if playback_surface is not None:
                    screen.blit(playback_surface, ui.get_playback_surface_pos())

                pygame.display.update()

            except Exception as e:
                Logger.error(f"Main loop error: {e}")

    finally:
        try:
            stream_handler.stop()
        except:
            pass

        try:
            event_bus.clear_all_subscribers()
        except:
            pass

        pygame.quit()
        Logger.info("=== END ===")


if __name__ == "__main__":
    main()
