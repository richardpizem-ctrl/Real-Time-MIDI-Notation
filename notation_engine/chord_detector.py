"""
Chord Detector – stabilná detekcia základných triád.

Podporované:
- dur (major)
- mol (minor)
- dim (diminished)
- aug (augmented)

Stabilizované (Fáza 4):
- ochrana pred None
- ochrana pred nevalidnými hodnotami
- bezpečné spracovanie pitch-classov
- fallback pri chybách
"""

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
    (0, 4, 7): "",       # major
    (0, 3, 7): "m",      # minor
    (0, 3, 6): "dim",    # diminished
    (0, 4, 8): "aug",    # augmented
}


def detect_chord(pitches: Iterable[int]) -> Optional[str]:
    """
    Stabilizovaná detekcia akordov.
    - Bezpečné spracovanie vstupu
    - Ochrana pred None
    - Ochrana pred nevalidnými hodnotami
    - Podpora základných triád
    """

    if pitches is None:
        return None

    # Pitch classes (0–11), odstránenie duplikátov
    try:
        pcs = sorted({
            int(p) % 12
            for p in pitches
            if isinstance(p, (int, float))
        })
    except Exception:
        return None

    if len(pcs) < 3:
        return None

    # Skúsime každý pitch ako root
    for root in pcs:
        try:
            intervals = sorted(((pc - root) % 12 for pc in pcs))
        except Exception:
            continue

        # Vyfiltrujeme len intervaly relevantné pre triády
        triad = tuple(i for i in intervals if i in (0, 3, 4, 6, 7, 8))

        if len(triad) < 3:
            continue

        # Zoberieme prvé tri intervaly (najnižšie)
        key = (triad[0], triad[1], triad[2])

        if key in TRIAD_PATTERNS:
            try:
                name = NOTE_NAMES.get(root)
                if not isinstance(name, str):
                    return None
                return name + TRIAD_PATTERNS[key]
            except Exception:
                return None

    return None


# ---------------------------------------------------------
# NO-OP API (pre UIManager kompatibilitu)
# ---------------------------------------------------------
def update_color(track_index: int, color_hex: str):
    return

def update_visibility(track_index: int, visible: bool):
    return

def set_active_track(track_index: int):
    return
