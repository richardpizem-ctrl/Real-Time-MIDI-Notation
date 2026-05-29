# =========================================================
# test_chords_extended.py – v4.3.0
# Stabilný test všetkých základných durových a molových akordov
# Kompatibilné s Notation Engine 4.3.0
# =========================================================

from notation_engine.chord_detector import detect_chord


def test_chord(notes, label):
    """Safely tests chord detection for a given list of MIDI notes."""
    try:
        if not isinstance(notes, (list, tuple)):
            print(f"[INVALID INPUT] {label}: {notes}")
            return

        # Convert all values to int safely
        try:
            notes_int = [int(n) for n in notes]
        except Exception:
            print(f"[INVALID NOTE VALUES] {label}: {notes}")
            return

        chord = detect_chord(notes_int)

        if chord:
            print(f"[OK] {label}: {notes_int} → {chord}")
        else:
            print(f"[NONE] {label}: {notes_int} → No chord detected")

    except Exception as e:
        print(f"[ERROR] {label}: {e}")


def main():
    print("=== TEST: EXTENDED CHORD DETECTION (v4.3.0) ===\n")

    # -----------------------------------------
    # 12 MAJOR CHORDS
    # -----------------------------------------
    major_chords = {
        "C major":  [60, 64, 67],
        "C# major": [61, 65, 68],
        "D major":  [62, 66, 69],
        "D# major": [63, 67, 70],
        "E major":  [64, 68, 71],
        "F major":  [65, 69, 72],
        "F# major": [66, 70, 73],
        "G major":  [67, 71, 74],
        "G# major": [68, 72, 75],
        "A major":  [69, 73, 76],
        "A# major": [70, 74, 77],
        "B major":  [71, 75, 78],
    }

    print("--- MAJOR CHORDS ---")
    for label, notes in major_chords.items():
        test_chord(notes, label)

    print("\n")

    # -----------------------------------------
    # 12 MINOR CHORDS
    # -----------------------------------------
    minor_chords = {
        "C minor":  [60, 63, 67],
        "C# minor": [61, 64, 68],
        "D minor":  [62, 65, 69],
        "D# minor": [63, 66, 70],
        "E minor":  [64, 67, 71],
        "F minor":  [65, 68, 72],
        "F# minor": [66, 69, 73],
        "G minor":  [67, 70, 74],
        "G# minor": [68, 71, 75],
        "A minor":  [69, 72, 76],
        "A# minor": [70, 73, 77],
        "B minor":  [71, 74, 78],
    }

    print("--- MINOR CHORDS ---")
    for label, notes in minor_chords.items():
        test_chord(notes, label)

    print("\n=== END ===")


if __name__ == "__main__":
    main()
