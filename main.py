import os
import pygame

from event_bus.event_bus import EventBus
from event_bus.event_types import (
    NOTE_RECORDED,
    TRACK_SELECTED,
    MIDI_EXPORT_REQUEST,
    MIDI_EXPORTED
)

from track_system.track_system import TrackSystem
from notation_processor.notation_processor import NotationProcessor

# UI + MIDI prepojenie
from ui.ui_manager import UIManager
from real_time_processing.stream_handler import StreamHandler
from midi_input.event_router import EventRouter

# EXPORT
from renderer.exporter import export_to_png, export_to_svg


# ---------------------------------------------------------
# TEST HANDLERY (ponechané podľa architektúry)
# ---------------------------------------------------------
def on_note_recorded(data):
    print(f"[TEST] NOTE_RECORDED event received: {data}")

def on_track_selected(data):
    print(f"[TEST] TRACK_SELECTED event received: {data}")

def on_midi_exported(data):
    print(f"[TEST] MIDI_EXPORTED event received: {data}")


# ---------------------------------------------------------
# HLAVNÁ FUNKCIA
# ---------------------------------------------------------
def main():
    print("=== REAL-TIME MIDI NOTATION START ===")

    # 0. Vycentrovanie okna (bezpečné)
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    pygame.init()

    # 1. Dynamické rozlíšenie + DOUBLEBUF + HWSURFACE
    info = pygame.display.Info()
    screen_width = min(info.current_w - 100, 1600)
    screen_height = min(info.current_h - 100, 900)

    screen = pygame.display.set_mode(
        (screen_width, screen_height),
        pygame.DOUBLEBUF | pygame.HWSURFACE
    )
    pygame.display.set_caption("SIRIUS MIDI Engine | v1.2.0")

    clock = pygame.time.Clock()

    # 2. EventBus
    event_bus = EventBus()

    # 3. Registrácia handlerov
    event_bus.subscribe(NOTE_RECORDED, on_note_recorded)
    event_bus.subscribe(TRACK_SELECTED, on_track_selected)
    event_bus.subscribe(MIDI_EXPORTED, on_midi_exported)

    # 4. TrackSystem + NotationProcessor
    track_system = TrackSystem(event_bus)
    notation_processor = NotationProcessor(track_system, event_bus)

    # 5. UI Manager
    ui = UIManager()

    # 6. EventRouter pre MIDI → EventBus → UI
    event_router = EventRouter(event_bus, piano_roll_ui=ui.piano_ui)

    # 7. MIDI Stream Handler
    stream_handler = StreamHandler(piano_roll_ui=ui.piano_ui)
    stream_handler.event_router = event_router

    # -----------------------------------------------------
    # 8. Spustenie UI slučky
    # -----------------------------------------------------
    running = True
    while running:

        # Delta time (dt)
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Globálne skratky
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    export_to_png(screen, "export.png")
                    print("[EXPORT] export.png uložený")

                if event.key == pygame.K_SPACE:
                    print("[PLAYBACK] Toggle playback")

        # Update logiky
        notation_processor.update(dt)

        # Render
        ui.render(screen, dt)
        pygame.display.flip()

    print("=== END ===")
    pygame.quit()


if __name__ == "__main__":
    main()
