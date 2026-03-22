from typing import Iterable, Optional
import math

MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]

NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


def rotate(lst, n):
    return lst[n:] + lst[:n]


def correlation(a, b):
    mean_a = sum(a) / len(a)
    mean_b = sum(b) / len(b)
    num = sum((x - mean_a) * (y - mean_b) for x, y in zip(a, b))
    den_a = math.sqrt(sum((x - mean_a) ** 2 for x in a))
    den_b = math.sqrt(sum((y - mean_b) ** 2 for y in b))
    if den_a == 0 or den_b == 0:
        return 0
    return num / (den_a * den_b)


def detect_key(pitches: Iterable[int]) -> Optional[str]:
    histogram = [0] * 12
    for p in pitches:
        histogram[p % 12] += 1

    if sum(histogram) == 0:
        return None

    best_key = None
    best_score = -999

    for i in range(12):
        major_rot = rotate(MAJOR_PROFILE, i)
        minor_rot = rotate(MINOR_PROFILE, i)

        score_major = correlation(histogram, major_rot)
        score_minor = correlation(histogram, minor_rot)

        if score_major > best_score:
            best_score = score_major
            best_key = NOTE_NAMES[i]

        if score_minor > best_score:
            best_score = score_minor
            best_key = NOTE_NAMES[i] + "m"

    return best_key
