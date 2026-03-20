from notation_engine.notation_processor import NotationProcessor
from core.track_manager import TrackSystem
import mido
import keyboard


def main():
    processor = NotationProcessor()
    tracks = TrackSystem()

    print("Prepínanie traktu: 1–9 alebo SHIFT+1–6 (10–16)")
    print("Čakám na MIDI vstup...")

    # Nájdeme MIDI vstupné zariadenie
    inputs = mido.get_input_names()
    if not inputs:
        print("Žiadny MIDI vstup nenájdený!")
        return

    midi_in = mido.open_input(inputs[0])
    print(f"Pripojené k MIDI zariadeniu: {inputs[0]}")

    # Hlavná slučka programu
    for msg in midi_in:

        # --- PREPÍNAČ TRAKTU CEZ KLÁVESNICU ---
        for i in range(1, 10):
            if keyboard.is_pressed(str(i)):
                tracks.set_active_track(i)

        for i in range(1, 7):
            if keyboard.is_pressed("shift+" + str(i)):
                tracks.set_active_track(9 + i)

        # --- SPRACOVANIE REÁLNEHO MIDI ---
        if msg.type in ["note_on", "note_off"]:
            event = tracks.build_note_event_for_active_track(
                note=msg.note,
                velocity=msg.velocity,
                event_type=msg.type,
                time=msg.time if hasattr(msg, "time") else 0.0
            )

            processor.process_midi_event(event)
            print(f"MIDI {msg.type} → nota {msg.note} → trakt {tracks.active_track_id}")

        # --- TESTOVACIA NOTA (voliteľné) ---
        if keyboard.is_pressed("n"):
            event = tracks.build_note_event_for_active_track(
                note=60,
                velocity=100,
                event_type="note_on",
                time=0.0
            )
            processor.process_midi_event(event)
            print(f"Odoslaná testovacia nota na trakt {tracks.active_track_id}")


if __name__ == "__main__":
    main()

