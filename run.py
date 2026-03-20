from notation_engine.notation_processor import NotationProcessor
from core.track_manager import TrackSystem
import keyboard


def main():
    # Inicializácia procesora notácie
    processor = NotationProcessor()

    # Inicializácia 16-traktového systému
    tracks = TrackSystem()

    print("Prepínanie traktu: stlač číslo 1–9 alebo SHIFT+1–6 pre traky 10–16")

    # Hlavná slučka programu
    while True:

        # --- PREPÍNAČ TRAKTU CEZ KLÁVESNICU ---

        # Traky 1–9 (klávesy 1–9)
        for i in range(1, 10):
            if keyboard.is_pressed(str(i)):
                tracks.set_active_track(i)

        # Traky 10–16 (SHIFT + 1–6)
        for i in range(1, 7):
            if keyboard.is_pressed("shift+" + str(i)):
                tracks.set_active_track(9 + i)

        # --- TESTOVACIA NOTA (len na ukážku) ---
        # Keď stlačíš klávesu "N", odošle testovaciu notu na aktívny trakt
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
