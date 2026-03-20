from notation_engine.notation_processor import NotationProcessor
from core.track_manager import TrackSystem


def main():
    # Inicializácia procesora notácie
    processor = NotationProcessor()

    # Inicializácia 16-traktového systému
    tracks = TrackSystem()

    # Nastavíme aktívny trakt (napr. 1)
    tracks.set_active_track(1)

    # Vytvoríme MIDI event pre aktívny trakt
    test_event = tracks.build_note_event_for_active_track(
        note=60,
        velocity=100,
        event_type="note_on",
        time=0.5
    )

    # Odošleme event do NotationProcessor
    processor.process_midi_event(test_event)


if __name__ == "__main__":
    main()

