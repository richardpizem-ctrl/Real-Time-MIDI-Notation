# =========================================================
# test_chords.py – v4.3.0
# Stabilný test základnej detekcie akordov
# Kompatibilné s Notation Engine 4.3.0
# =========================================================

from notation_engine.chord_detector import detect_chord


def test_chord(notes):
    """Safely tests chord detection for a given list of MIDI notes."""
    try:
        if not isinstance(notes, (list, tuple)):
            print(f"[INVALID INPUT] {notes}")
            return

        # Convert all values to int safely
        try:
            notes_int = [int(n) for n in notes]
        except Exception:
            print(f"[INVALID NOTE VALUES] {notes}")
            return

        chord = detect_chord(notes_int)

        if chord:
            print(f"[OK] Notes {notes_int} → Detected chord: {chord}")
        else:
            print(f"[NONE] Notes {notes_int} → No chord detected")

    except Exception as e:
        print(f"[ERROR] While testing notes {notes}: {e}")


def main():
    print("=== TEST: BASIC CHORD DETECTION (v4.3.0) ===")

    # Basic triads
    test_chord([60, 64, 67])   # C major
    test_chord([57, 60, 64])   # A minor
    test_chord([62, 65, 69])   # D major

    # Edge cases
    test_chord([60])           # Single note
    test_chord([60, 61])       # No chord
    test_chord(["x", 64, 67])  # Invalid input

    print("=== END ===")


if __name__ == "__main__":
    main()
