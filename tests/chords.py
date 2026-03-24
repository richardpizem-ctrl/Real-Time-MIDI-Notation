# test_chords.py – základný test detekcie akordov

from notation_engine.chord_detector import detect_chord


def test_chord(notes):
    chord = detect_chord(notes)
    if chord:
        print(f"Notes {notes} → Detected chord: {chord.name}")
    else:
        print(f"Notes {notes} → No chord detected")


def main():
    print("=== TEST: BASIC CHORD DETECTION ===")

    test_chord([60, 64, 67])  # C major
    test_chord([57, 60, 64])  # A minor
    test_chord([62, 65, 69])  # D major

    print("=== END ===")


if __name__ == "__main__":
    main()
