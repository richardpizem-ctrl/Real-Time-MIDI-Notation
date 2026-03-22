# notation_engine/chord_detector.py

from typing import Iterable, Optional

NOTE_NAMES = {
    0: "C",
    1: "C#",
    2: "D",
    3: "D#",
    4: "E",
    5: "F",
    6: "F#",
    7: "G",
    8: "G#",
    9: "A",
    10: "A#",
    11: "B",
}

TRIAD_PATTERNS = {
    (0, 4, 7): "",
    (0, 3, 7): "m",
    (0, 3, 6): "dim",
    (0, 4, 8): "aug",
}


def detect_chord(pitches: Iterable[int]) -> Optional[str]:
    pcs = sorted({p % 12 for p in pitches})
    if len(pcs) < 3:
        return None

    for root in pcs:
        intervals = sorted(((pc - root) % 12 for pc in pcs))
        triad = tuple(i for i in intervals if i in (0, 3, 4, 6, 7, 8))
        if len(triad) < 3:
            continue

        key = (triad[0], triad[1], triad[2])
        if key in TRIAD_PATTERNS:
            return NOTE_NAMES[root] + TRIAD_PATTERNS[key]

    return None
