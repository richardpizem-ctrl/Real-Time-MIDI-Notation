# =========================================================
# test_chords.py v2.0.0
# Stabilný test detekcie akordov pre Real-Time MIDI Notation
# =========================================================

from notation_engine.chord_detector import detect_chord
from core.logger import Logger


def test_chord(notes):
    """
    Bezpečne otestuje detekciu akordu pre danú množinu MIDI tónov.
    Real‑time safe: žiadne výnimky nesmú preraziť.
    """
    try:
        if not isinstance(notes, (list, tuple)):
            Logger.error(f"Invalid notes input: {notes}")
            return

        chord = detect_chord(notes)

        if chord:
            Logger.info(f"Notes {notes} → Detected chord: {chord.name}")
        else:
            Logger.info(f"Notes {notes} → No chord detected")

    except Exception as e:
        Logger.error(f"Chord detection error for notes {notes}: {e}")


def main():
    Logger.info("=== TEST: CHORD DETECTION v2.0.0 ===")

    # C major (C–E–G)
    test_chord([60, 64, 67])

    # A minor (A–C–E)
    test_chord([57, 60, 64])

    # D major (D–F#–A)
    test_chord([62, 65, 69])

    # Edge cases
    test_chord([])               # empty
    test_chord([60])             # single note
    test_chord([60, 61, 62])     # cluster
    test_chord("invalid_input")  # invalid

    Logger.info("=== END ===")


if __name__ == "__main__":
    main()
