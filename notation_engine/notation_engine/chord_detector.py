from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Chord:
    name: str
    root: int          # 0–11 (C–H)
    quality: str       # "maj", "min", "dim", "aug", "sus2", "sus4"
    notes: List[int]   # normalizované tóny (0–11)


# Základné šablóny akordov (intervaly od základného tónu)
CHORD_TEMPLATES = {
    "maj":  [0, 4, 7],
    "min":  [0, 3, 7],
    "dim":  [0, 3, 6],
    "aug":  [0, 4, 8],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
}


NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F",
              "F#", "G", "G#", "A", "A#", "B"]


def normalize_notes(notes: List[int]) -> List[int]:
    """
    Vezme MIDI noty (napr. 60, 64, 67) a vráti ich v rozsahu 0–11 (C–H).
    """
    return sorted(list({n % 12 for n in notes}))


def detect_chord(active_notes: List[int]) -> Optional[Chord]:
    """
    Zoznam aktuálne stlačených MIDI nôt (napr. [60, 64, 67])
    → vráti Chord alebo None, ak nič nesedí.
    """
    if len(active_notes) < 3:
        return None

    normalized = normalize_notes(active_notes)

    for root in normalized:
        intervals = sorted(((n - root) % 12 for n in normalized))

        for quality, template in CHORD_TEMPLATES.items():
            if intervals == template:
                name = f"{NOTE_NAMES[root]}{quality}"
                return Chord(
                    name=name,
                    root=root,
                    quality=quality,
                    notes=normalized,
                )

    return None
