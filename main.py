from event_bus.event_bus import EventBus
from event_bus.event_types import (
    NOTE_RECORDED,
    TRACK_SELECTED,
    MIDI_EXPORT_REQUEST,
    MIDI_EXPORTED
)
from track_system.track_system import TrackSystem
from notation_processor.notation_processor import NotationProcessor


def on_note_recorded(data):
    print(f"[TEST] NOTE_RECORDED event received: {data}")

def on_track_selected(data):
    print(f"[TEST] TRACK_SELECTED event received: {data}")

def on_midi_exported(data):
    print(f"[TEST] MIDI_EXPORTED event received: {data}")


def main():
    print("=== TEST START ===")

    # 1. Vytvoríme EventBus
    event_bus = EventBus()

    # 2. Registrujeme testovacie handlery
    event_bus.subscribe(NOTE_RECORDED, on_note_recorded)
    event_bus.subscribe(TRACK_SELECTED, on_track_selected)
    event_bus.subscribe(MIDI_EXPORTED, on_midi_exported)

    # 3. Vytvoríme TrackSystem a NotationProcessor
    track_system = TrackSystem(event_bus)
    notation_processor = NotationProcessor(track_system, event_bus)

    # 4. Simulujeme výber tracku
    print("\n--- Selecting track 1 ---")
    track_system.select_track(1)

    # 5. Simulujeme nahratie noty
    print("\n--- Recording note C4 ---")
    track_system.record_note(
        track_id=1,
        note="C4",
        velocity=100,
        timestamp=123.45
    )

    # 6. Simulujeme export MIDI
    print("\n--- Requesting MIDI export ---")
    event_bus.publish(MIDI_EXPORT_REQUEST, {"filename": "test_output.mid"})

    print("\n=== TEST END ===")


if __name__ == "__main__":
    main()
