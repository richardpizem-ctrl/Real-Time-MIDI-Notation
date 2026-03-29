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
    """
    Stabilizovaná detekcia akordov.
    - Bezpečné spracovanie vstupu
    - Ochrana pred None
    - Ochrana pred nevalidnými hodnotami
    - Podpora základných triád
    """

    # Validate input
    if pitches is None:
        return None

    try:
        pcs = sorted({int(p) % 12 for p in pitches if isinstance(p, (int, float))})
    except Exception:
        return None

    if len(pcs) < 3:
        return None

    # Try each pitch as root
    for root in pcs:
        try:
            intervals = sorted(((pc - root) % 12 for pc in pcs))
        except Exception:
            continue

        # Filter only triad-relevant intervals
        triad = tuple(i for i in intervals if i in (0, 3, 4, 6, 7, 8))

        if len(triad) < 3:
            continue

        key = (triad[0], triad[1], triad[2])

        if key in TRIAD_PATTERNS:
            try:
                return NOTE_NAMES[root] + TRIAD_PATTERNS[key]
            except Exception:
                return None

    return None
