from typing import Iterable, Optional

# ---------------------------------------------------------
# DEFINÍCIA MODÁLNYCH STUPNÍC (IONIAN → LOCRIAN)
# ---------------------------------------------------------
MODES = {
    "ionian":      [0, 2, 4, 5, 7, 9, 11],   # major
    "dorian":      [0, 2, 3, 5, 7, 9, 10],
    "phrygian":    [0, 1, 3, 5, 7, 8, 10],
    "lydian":      [0, 2, 4, 6, 7, 9, 11],
    "mixolydian":  [0, 2, 4, 5, 7, 9, 10],
    "aeolian":     [0, 2, 3, 5, 7, 8, 10],   # natural minor
    "locrian":     [0, 1, 3, 5, 6, 8, 10],
}

# ---------------------------------------------------------
# PENTATONIKY
# ---------------------------------------------------------
PENTATONICS = {
    "major_pent":  [0, 2, 4, 7, 9],
    "minor_pent":  [0, 3, 5, 7, 10],
}

# ---------------------------------------------------------
# BLUES SCALE
# ---------------------------------------------------------
BLUES = {
    "blues": [0, 3, 5, 6, 7, 10],
}

ALL_SCALES = {**MODES, **PENTATONICS, **BLUES}


def detect_scale(
    pitches: Iterable[int],
    current_chord: Optional[str],
    current_key: Optional[str]
) -> Optional[tuple[str, int]]:
    """
    Vráti tuple (scale_name, root_pitch_class)
    Napr.: ("dorian", 2) → D dorian
    """

    pcs = sorted({p % 12 for p in pitches})
    if not pcs:
        return None

    # ---------------------------------------------------------
    # 1) Ak máme akord → root akordu je silný kandidát na root stupnice
    # ---------------------------------------------------------
    chord_root = None
    if current_chord:
        root = current_chord[0]
        if len(current_chord) > 1 and current_chord[1] in ("#", "b"):
            root = current_chord[:2]

        pitch_map = {
            "C": 0, "C#": 1, "Db": 1,
            "D": 2, "D#": 3, "Eb": 3,
            "E": 4, "F": 5, "F#": 6, "Gb": 6,
            "G": 7, "G#": 8, "Ab": 8,
            "A": 9, "A#": 10, "Bb": 10,
            "B": 11,
        }
        chord_root = pitch_map.get(root, None)

    # ---------------------------------------------------------
    # 2) Ak máme key detection → root tóniny je ďalší kandidát
    # ---------------------------------------------------------
    key_root = None
    if current_key:
        parts = current_key.split()
        if len(parts) == 2:
            note_name, _ = parts
            pitch_map = {
                "C": 0, "C#": 1, "Db": 1,
                "D": 2, "D#": 3, "Eb": 3,
                "E": 4, "F": 5, "F#": 6, "Gb": 6,
                "G": 7, "G#": 8, "Ab": 8,
                "A": 9, "A#": 10, "Bb": 10,
                "B": 11,
            }
            key_root = pitch_map.get(note_name, None)

    # ---------------------------------------------------------
    # 3) Skúšame všetky možné stupnice pre všetky možné rooty
    # ---------------------------------------------------------
    candidates = []

    for root in range(12):
        for scale_name, intervals in ALL_SCALES.items():
            scale_pcs = {(root + i) % 12 for i in intervals}

            # skóre = koľko hraných tónov patrí do stupnice
            score = len([pc for pc in pcs if pc in scale_pcs])

            # bonus za zhodu s akordom
            if chord_root is not None and chord_root == root:
                score += 2

            # bonus za zhodu s key detection
            if key_root is not None and key_root == root:
                score += 1

            candidates.append((score, scale_name, root))

    # vyber najlepšiu stupnicu
    best = max(candidates, key=lambda x: x[0])
    _, scale_name, root = best

    return scale_name, root
