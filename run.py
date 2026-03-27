# run.py – hlavný spúšťací súbor pre Real-Time MIDI Notation

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


# ---------------------------------------------------------
# TEST HANDLERY (ponechané podľa tvojej architektúry)
# ---------------------------------------------------------
def on_note_recorded(data):
    print(f"[TEST] NOTE_RECORDED event received: {data}")

def on_track_selected(data):
    print(f"[TEST] TRACK_SELECTED event received: {data}")

def on_midi_exported(data):
    print(f"[TEST] MIDI_EXPORTED event received: {data}")

def on_error(data):
    print(f"[TEST] ERROR_OCCURRED: {data}")


# ---------------------------------------------------------
# HLAVNÁ FUNKCIA
# ---------------------------------------------------------
def main():
    print("=== REAL-TIME MIDI NOTATION START ===")

    # 1. EventBus
    event_bus = EventBus()

    # 2. Registrácia handlerov
    event_bus.subscribe(NOTE_RECORDED, on_note_recorded)
    event_bus.subscribe(TRACK_SELECTED, on_track_selected)
    event_bus.subscribe(MIDI_EXPORTED, on_midi_exported)
    event_bus.subscribe(ERROR_OCCURRED, on_error)

    # 3. TrackSystem + NotationProcessor
    track_system = TrackSystem(event_bus)
    notation_processor = NotationProcessor(track_system, event_bus)

    # 4. UI Manager
    ui = UIManager()

    # 5. EventRouter pre MIDI → EventBus → UI
    event_router = EventRouter(
        event_bus=event_bus,
        piano_roll_ui=ui.piano_ui
    )

    # 6. MIDI Stream Handler prepojený s Piano Roll UI + EventRouter
    stream_handler = StreamHandler(
        piano_roll_ui=ui.piano_ui,
        event_router=event_router
    )

    # -----------------------------------------------------
    # 7. Spustenie UI slučky
    # -----------------------------------------------------
    ui.run()

    print("=== END ===")


if __name__ == "__main__":
    main()
