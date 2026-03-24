# test_chords_extended.py – Test všetkých základných durových a molových akordov

from notation_engine.chord_detector import detect_chord


def test_chord(notes):
    chord = detect_chord(notes)
    if chord:
        print(f"Notes {notes} → Detected chord: {chord.name}")
    else:
        print(f"Notes {notes} → No chord detected")


def main():
    print("=== TEST: EXTENDED CHORD DETECTION ===\n")

    # -----------------------------------------
    # 12 MAJOR CHORDS (C, C#, D, D#, E, F, F#, G, G#, A, A#, B)
    # -----------------------------------------
    major_chords = {
        "C":  [60, 64, 67],
        "C#": [61, 65, 68],
        "D":  [62, 66, 69],
        "D#": [63, 67, 70],
        "E":  [64, 68, 71],
        "F":  [65, 69, 72],
        "F#": [66, 70, 73],
        "G":  [67, 71, 74],
        "G#": [68, 72, 75],
        "A":  [69, 73, 76],
        "A#": [70, 74, 77],
        "B":  [71, 75, 78],
    }

    print("--- MAJOR CHORDS ---")
    for name, notes in major_chords.items():
        test_chord(notes)

    print("\n")

    # -----------------------------------------
    # 12 MINOR CHORDS (Cm, C#m, Dm, D#m, Em, Fm, F#m, Gm, G#m, Am, A#m, Bm)
    # -----------------------------------------
    minor_chords = {
        "Cm":  [60, 63, 67],
        "C#m": [61, 64, 68],
        "Dm":  [62, 65, 69],
        "D#m": [63, 66, 70],
        "Em":  [64, 67, 71],
        "Fm":  [65, 68, 72],
        "F#m": [66, 69, 73],
        "Gm":  [67, 70, 74],
        "G#m": [68, 71, 75],
        "Am":  [69, 72, 76],
        "A#m": [70, 73, 77],
        "Bm":  [71, 74, 78],
    }

    print("--- MINOR CHORDS ---")
    for name, notes in minor_chords.items():
        test_chord(notes)

    print("\n=== END ===")


if __name__ == "__main__":
    main()
