# test_chords.py – Test detekcie akordov v projekte Real-Time MIDI Notation

from notation_engine.chord_detector import detect_chord
from core.logger import Logger


def test_chord(notes):
    """Otestuje detekciu akordu pre danú množinu tónov."""
    try:
        chord = detect_chord(notes)
    except Exception as e:
        Logger.error(f"Chord detection error for notes {notes}: {e}")
        return

    if chord:
        Logger.info(f"Notes {notes} → Detected chord: {chord.name}")
    else:
        Logger.info(f"Notes {notes} → No chord detected")


def main():
    Logger.info("=== TEST: CHORD DETECTION ===")

    # C major (C–E–G)
    test_chord([60, 64, 67])

    # A minor (A–C–E)
    test_chord([57, 60, 64])

    # D major (D–F#–A)
    test_chord([62, 65, 69])

    Logger.info("=== END ===")


if __name__ == "__main__":
    main()
