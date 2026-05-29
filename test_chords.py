# =========================================================
# test_chords.py v4.3.0
# Stable chord detection test for Real-Time MIDI Notation
# =========================================================

from notation_engine.chord_detector import detect_chord
from core.logger import Logger


def test_chord(notes):
    """
    Safely test chord detection for a given MIDI note set.
    Real-time safe: no exceptions allowed.
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
    Logger.info("=== TEST: CHORD DETECTION v4.3.0 ===")

    # Basic triads
    test_chord([60, 64, 67])   # C major
    test_chord([57, 60, 64])   # A minor
    test_chord([62, 65, 69])   # D major

    # Edge cases
    test_chord([])               # empty
    test_chord([60])             # single note
    test_chord([60, 61, 62])     # cluster
    test_chord("invalid_input")  # invalid

    Logger.info("=== END ===")


if __name__ == "__main__":
    main()
