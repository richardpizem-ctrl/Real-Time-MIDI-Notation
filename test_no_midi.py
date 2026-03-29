# test_no_midi.py – Test systému bez MIDI zariadení

from event_bus.event_bus import EventBus
from event_bus.event_types import NOTE_RECORDED, TRACK_SELECTED

from track_system.track_system import TrackSystem
from notation_processor.notation_processor import NotationProcessor

from real_time_processing.stream_handler import StreamHandler
from midi_input.event_router import EventRouter

from core.logger import Logger


def main():
    Logger.info("=== TEST: NO MIDI DEVICES ===")

    # 1. EventBus
    try:
        event_bus = EventBus()
    except Exception as e:
        Logger.error(f"Failed to initialize EventBus: {e}")
        return

    # 2. TrackSystem + NotationProcessor
    try:
        track_system = TrackSystem(event_bus)
        notation_processor = NotationProcessor(track_system, event_bus)
    except Exception as e:
        Logger.error(f"Failed to initialize TrackSystem or NotationProcessor: {e}")
        return

    # 3. UI nie je potrebné – testujeme len MIDI pipeline
    try:
        event_router = EventRouter(event_bus, piano_roll_ui=None)
        stream_handler = StreamHandler(piano_roll_ui=None)
        stream_handler.event_router = event_router
    except Exception as e:
        Logger.error(f"Failed to initialize EventRouter or StreamHandler: {e}")
        return

    # 4. Simulovaný MIDI event
    fake_event = {
        "type": "note_on",
        "note": 64,
        "velocity": 90,
        "timestamp": 0.0
    }

    Logger.info("[TEST] Spracovávam simulovaný MIDI event...")
    try:
        stream_handler.process_midi_message(fake_event)
    except Exception as e:
        Logger.error(f"Error processing fake note_on event: {e}")

    # 5. Simulovaný NOTE_OFF
    fake_event_off = {
        "type": "note_off",
        "note": 64,
        "velocity": 0,
        "timestamp": 0.1
    }

    try:
        stream_handler.process_midi_message(fake_event_off)
    except Exception as e:
        Logger.error(f"Error processing fake note_off event: {e}")

    Logger.info("[TEST] Test úspešne dokončený.")


if __name__ == "__main__":
    main()
