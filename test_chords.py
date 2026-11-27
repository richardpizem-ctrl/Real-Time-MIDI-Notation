# =========================================================
# test_chords.py v4.3.0
# Stable chord detection test for Real-Time MIDI Notation
# =========================================================

from notation_engine.chord_detector import detect_chord
from core.logger import Logger


def show_chord(notes):
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
    show_chord([60, 64, 67])   # C major
    show_chord([57, 60, 64])   # A minor
    show_chord([62, 65, 69])   # D major

    # Edge cases
    show_chord([])               # empty
    show_chord([60])             # single note
    show_chord([60, 61, 62])     # cluster
    show_chord("invalid_input")  # invalid

    Logger.info("=== END ===")


if __name__ == "__main__":
    main()
