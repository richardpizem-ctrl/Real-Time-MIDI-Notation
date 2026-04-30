# test_midi_listener_no_device.py – Test MIDIListener bez MIDI zariadení (v2.0.0)

from core.logger import Logger
from core.event_bus import EventBus
from core.event_types import NOTE_RECORDED, ERROR_OCCURRED

from core.track_manager import TrackManager
from core.notation_processor import NotationProcessor
from midi_input.midi_listener import MIDIListener


def on_note_recorded(data):
    Logger.info(f"[TEST] NOTE_RECORDED received: {data}")


def on_error(msg):
    Logger.error(f"[TEST] ERROR_OCCURRED: {msg}")


def main():
    Logger.info("=== TEST: MIDIListener WITHOUT MIDI DEVICE (v2.0.0) ===")

    # -----------------------------------------------------
    # 1. EventBus
    # -----------------------------------------------------
    event_bus = EventBus()
    event_bus.subscribe(NOTE_RECORDED, on_note_recorded)
    event_bus.subscribe(ERROR_OCCURRED, on_error)

    # -----------------------------------------------------
    # 2. TrackManager + NotationProcessor
    # -----------------------------------------------------
    track_manager = TrackManager(event_bus=event_bus)
    notation_processor = NotationProcessor(
        track_manager=track_manager,
        event_bus=event_bus
    )

    # -----------------------------------------------------
    # 3. MIDIListener (bez fyzického zariadenia)
    # -----------------------------------------------------
    midi_listener = MIDIListener(event_bus=event_bus)

    # Simulujeme, že žiadne zariadenia nie sú dostupné
    midi_listener.available_inputs = []
    midi_listener.selected_input = None

    Logger.info("[TEST] MIDIListener initialized with NO devices.")

    # -----------------------------------------------------
    # 4. Simulovaný NOTE_ON event
    # -----------------------------------------------------
    fake_note_on = {
        "type": "note_on",
        "note": 64,
        "velocity": 90,
        "time": 0.0
    }

    Logger.info("[TEST] Sending fake NOTE_ON event...")
    midi_listener.handle_message(fake_note_on)

    # -----------------------------------------------------
    # 5. Simulovaný NOTE_OFF event
    # -----------------------------------------------------
    fake_note_off = {
        "type": "note_off",
        "note": 64,
        "velocity": 0,
        "time": 0.1
    }

    Logger.info("[TEST] Sending fake NOTE_OFF event...")
    midi_listener.handle_message(fake_note_off)

    Logger.info("=== TEST COMPLETED SUCCESSFULLY ===")


if __name__ == "__main__":
    main()
