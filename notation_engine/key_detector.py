"""
Key Detector – stabilná detekcia tóniny podľa Krumhansl-Schmuckler profilu.

Stabilizované:
- ochrana pred None a nevalidnými pitchmi
- bezpečné výpočty korelácie
- fallback pri chybách
- jednotné návratové hodnoty
"""

from typing import Iterable, Optional
import math

# Krumhansl-Schmuckler key profiles
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------
def rotate(lst, n):
    """Bezpečná rotácia listu."""
    try:
        n = int(n) % len(lst)
        return lst[n:] + lst[:n]
    except Exception:
        return lst


def correlation(a, b):
    """Pearsonova korelácia – stabilná verzia."""
    try:
        mean_a = sum(a) / len(a)
        mean_b = sum(b) / len(b)

        num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
        den_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
        den_b = math.sqrt(sum((y - mean_b) ** 2 for y in b))

        if den_a == 0 or den_b == 0:
            return 0.0

        return num / (den_a * den_b)
    except Exception:
        return 0.0


# ---------------------------------------------------------
# MAIN KEY DETECTION
# ---------------------------------------------------------
def detect_key(pitches: Iterable[int]) -> Optional[str]:
    """
    Detekcia tóniny podľa histogramu pitch-classov.
    Vráti napr. "C", "G#", "Am", "F#m".
    """

    if pitches is None:
        return None

    # Histogram pitch-classov
    histogram = [0] * 12

    try:
        for p in pitches:
            if isinstance(p, (int, float)):
                histogram[int(p) % 12] += 1
    except Exception:
        return None

    if sum(histogram) == 0:
        return None

    best_key = None
    best_score = -999.0

    # Pre každý možný root (0–11)
    for i in range(12):
        try:
            major_rot = rotate(MAJOR_PROFILE, i)
            minor_rot = rotate(MINOR_PROFILE, i)

            score_major = correlation(histogram, major_rot)
            score_minor = correlation(histogram, minor_rot)

            # Major
            if score_major > best_score:
                best_score = score_major
                best_key = NOTE_NAMES[i]

            # Minor
            if score_minor > best_score:
                best_score = score_minor
                best_key = NOTE_NAMES[i] + "m"

        except Exception:
            continue

    return best_key
