# =========================================================
# ScaleDetector v4.3.0
# Stabilná detekcia stupnice podľa pitch-classov
# Real-time safe, deterministické, optimalizované
# =========================================================

from typing import Iterable, Optional, Dict, Set, Any

NOTE_NAMES = [
    "C", "C#", "D", "D#", "E", "F",
    "F#", "G", "G#", "A", "A#", "B"
]

MAJOR_PATTERN = [0, 2, 4, 5, 7, 9, 11]
MINOR_PATTERN = [0, 2, 3, 5, 7, 8, 10]


# ---------------------------------------------------------
# SAFE HELPERS
# ---------------------------------------------------------
def _safe_iter_pitches(pitches: Any) -> Iterable[int]:
    if pitches is None or not hasattr(pitches, "__iter__"):
        return []
    result = []
    append = result.append
    for p in pitches:
        try:
            if isinstance(p, (int, float)):
                append(int(p) % 12)
        except Exception:
            continue
    return result


def _build_scale(root: int, is_major: bool) -> Set[int]:
    try:
        root = int(root) % 12
    except Exception:
        return set()
    pattern = MAJOR_PATTERN if is_major else MINOR_PATTERN
    return {(root + step) % 12 for step in pattern}


# ---------------------------------------------------------
# SCALE DETECTOR v4.3.0
# ---------------------------------------------------------
class ScaleDetector:
    """
    ScaleDetector (v4.3.0):
    - analyzuje MIDI pitch-classy
    - odhaduje stupnicu (dur/mol)
    - vracia:
        root (0–11)
        is_major (bool)
        name ("C major", "A minor")
        scale_pcs (set)
        coverage (0.0–1.0)
    - real-time safe, deterministické
    """

    __slots__ = ("scales",)

    def __init__(self):
        scales = []
        append = scales.append

        for root in range(12):
            append({
                "root": root,
                "is_major": True,
                "name": f"{NOTE_NAMES[root]} major",
                "pcs": _build_scale(root, True),
            })
            append({
                "root": root,
                "is_major": False,
                "name": f"{NOTE_NAMES[root]} minor",
                "pcs": _build_scale(root, False),
            })

        self.scales = scales

    # ---------------------------------------------------------
    # DETEKCIA STUPNICE
    # ---------------------------------------------------------
    def detect_scale(self, pitches: Iterable[int]) -> Optional[Dict[str, Any]]:
        pcs = set(_safe_iter_pitches(pitches))
        if not pcs:
            return None

        best = None
        best_score = -1.0

        for scale in self.scales:
            scale_pcs = scale["pcs"]
            intersection = pcs.intersection(scale_pcs)
            if not intersection:
                continue

            try:
                coverage = len(intersection) / max(len(pcs), 1)
            except Exception:
                coverage = 0.0

            if coverage > best_score:
                best_score = coverage
                best = {
                    "root": scale["root"],
                    "is_major": scale["is_major"],
                    "name": scale["name"],
                    "scale_pcs": set(scale_pcs),
                    "coverage": float(coverage),
                }

        return best

    # ---------------------------------------------------------
    # ANALÝZA PITCHOV VOČI STUPNICI
    # ---------------------------------------------------------
    def analyze_pitches_in_scale(
        self,
        pitches: Iterable[int],
        scale_root: Optional[int] = None,
        is_major: bool = True,
    ) -> Dict[int, str]:

        pcs_list = list(_safe_iter_pitches(pitches))
        roles: Dict[int, str] = {}

        if not pcs_list:
            return roles

        if scale_root is None:
            detected = self.detect_scale(pcs_list)
            if not detected:
                for p in pcs_list:
                    roles[p] = "outside"
                return roles
            scale_pcs = detected["scale_pcs"]
        else:
            scale_pcs = _build_scale(scale_root, is_major)

        for p in pcs_list:
            roles[p] = "in_scale" if p in scale_pcs else "outside"

        return roles
