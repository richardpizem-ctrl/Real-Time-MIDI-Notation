"""
Harmony Engine – stabilná harmonická analýza pre Real-Time-MIDI-Notation.

ÚLOHA:
- dostať informáciu o kľúči (tonalite) a akorde
- analyzovať MIDI pitch hodnoty
- vrátiť harmonickú rolu:
    - root
    - chord_tone
    - tension
    - scale_tone
    - outside
"""

from typing import List, Dict, Optional


class HarmonyRole:
    ROOT = "root"
    CHORD_TONE = "chord_tone"
    TENSION = "tension"
    SCALE_TONE = "scale_tone"
    OUTSIDE = "outside"


class HarmonyEngine:
    """
    Stabilizovaný harmonický engine (Fáza 4).
    """

    def __init__(self):
        self.chord_intervals = {
            HarmonyRole.ROOT: {0},
            HarmonyRole.CHORD_TONE: {3, 4, 7, 10, 11},
            HarmonyRole.TENSION: {1, 2, 5, 6, 8, 9},
        }

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    @staticmethod
    def _normalize_pitch(pitch: int) -> int:
        try:
            return int(pitch) % 12
        except Exception:
            return 0

    @staticmethod
    def _build_scale(key_root: int, is_major: bool = True) -> List[int]:
        try:
            key_root = int(key_root) % 12
        except Exception:
            return []

        if is_major:
            pattern = [0, 2, 4, 5, 7, 9, 11]
        else:
            pattern = [0, 2, 3, 5, 7, 8, 10]

        try:
            return [(key_root + step) % 12 for step in pattern]
        except Exception:
            return []

    # ---------------------------------------------------------
    # MAIN ANALYSIS
    # ---------------------------------------------------------
    def analyze(
        self,
        pitches: List[int],
        key_root: Optional[int] = None,
        is_major: bool = True,
        chord_root: Optional[int] = None,
    ) -> Dict[int, str]:

        roles: Dict[int, str] = {}

        if not isinstance(pitches, list):
            return roles

        # Stupnica
        scale_pitches: List[int] = []
        if key_root is not None:
            scale_pitches = self._build_scale(key_root, is_major)

        # Normalizovaný root akordu
        chord_root_norm = None
        if chord_root is not None:
            try:
                chord_root_norm = int(chord_root) % 12
            except Exception:
                chord_root_norm = None

        for p in pitches:
            try:
                norm = self._normalize_pitch(p)
            except Exception:
                roles[p] = HarmonyRole.OUTSIDE
                continue

            # 1) ROOT akordu
            if chord_root_norm is not None:
                try:
                    interval = (norm - chord_root_norm) % 12
                except Exception:
                    roles[p] = HarmonyRole.OUTSIDE
                    continue

                if interval in self.chord_intervals[HarmonyRole.ROOT]:
                    roles[p] = HarmonyRole.ROOT
                    continue

                if interval in self.chord_intervals[HarmonyRole.CHORD_TONE]:
                    roles[p] = HarmonyRole.CHORD_TONE
                    continue

                if interval in self.chord_intervals[HarmonyRole.TENSION]:
                    roles[p] = HarmonyRole.TENSION
                    continue

            # 4) SCALE TONE vs OUTSIDE
            if scale_pitches:
                roles[p] = (
                    HarmonyRole.SCALE_TONE
                    if norm in scale_pitches
                    else HarmonyRole.OUTSIDE
                )
            else:
                roles[p] = HarmonyRole.OUTSIDE

        return roles

    # ---------------------------------------------------------
    # ANALÝZA Z NOTE OBJEKTOV
    # ---------------------------------------------------------
    def analyze_notes(
        self,
        notes: List[object],
        key_root: Optional[int] = None,
        is_major: bool = True,
        chord_root: Optional[int] = None,
        pitch_attr: str = "pitch",
    ) -> Dict[object, str]:

        if not isinstance(notes, list):
            return {}

        pitches = []
        for n in notes:
            try:
                if hasattr(n, pitch_attr):
                    pitches.append(int(getattr(n, pitch_attr)))
            except Exception:
                continue

        pitch_roles = self.analyze(
            pitches=pitches,
            key_root=key_root,
            is_major=is_major,
            chord_root=chord_root,
        )

        result: Dict[object, str] = {}
        for n in notes:
            if hasattr(n, pitch_attr):
                try:
                    p = int(getattr(n, pitch_attr))
                    result[n] = pitch_roles.get(p, HarmonyRole.OUTSIDE)
                except Exception:
                    result[n] = HarmonyRole.OUTSIDE
            else:
                result[n] = HarmonyRole.OUTSIDE

        return result


# ---------------------------------------------------------
# NO-OP API (pre UIManager kompatibilitu)
# ---------------------------------------------------------
def update_color(track_index: int, color_hex: str):
    return

def update_visibility(track_index: int, visible: bool):
    return

def set_active_track(track_index: int):
    return
