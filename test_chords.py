# test_chords.py – Test detekcie akordov v projekte Real-Time MIDI Notation

from notation_engine.chord_detector import detect_chord


def test_chord(notes):
    chord = detect_chord(notes)
    if chord:
        print(f"Notes {notes} → Detected chord: {chord.name}")
    else:
        print(f"Notes {notes} → No chord detected")


def main():
    print("=== TEST: CHORD DETECTION ===")

    # C major (C–E–G)
    test_chord([60, 64, 67])

    # A minor (A–C–E)
    test_chord([57, 60, 64])

    # D major (D–F#–A)
    test_chord([62, 65, 69])

    print("=== END ===")


if __name__ == "__main__":
    main()
