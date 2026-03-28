# notation_engine/harmony_engine.py

from typing import List, Dict, Optional, Tuple


class HarmonyRole:
    ROOT = "root"
    CHORD_TONE = "chord_tone"
    TENSION = "tension"
    SCALE_TONE = "scale_tone"
    OUTSIDE = "outside"


class HarmonyEngine:
    """
    Všeobecný harmonický engine.

    ÚLOHA:
    - dostať informáciu o aktuálnom kľúči (tonalite) a akorde
    - dostať zoznam tónov (MIDI pitch)
    - vrátiť pre každý tón jeho harmonickú rolu:
        - root
        - chord_tone (3, 5, 7)
        - tension (9, 11, 13)
        - scale_tone (v stupnici, ale mimo akordu)
        - outside (mimo stupnice)
    """

    def __init__(self):
        # Intervaly v poltónoch voči rootu akordu
        self.chord_intervals = {
            HarmonyRole.ROOT: {0},
            HarmonyRole.CHORD_TONE: {3, 4, 7, 10, 11},  # m3, M3, 5, b7, M7
            HarmonyRole.TENSION: {1, 2, 5, 6, 8, 9},    # b9, 9, 11, #11, b13, 13
        }

    # ---------------------------------------------------------
    # POMOCNÉ FUNKCIE
    # ---------------------------------------------------------
    @staticmethod
    def _normalize_pitch(pitch: int) -> int:
        return pitch % 12

    @staticmethod
    def _build_scale(key_root: int, is_major: bool = True) -> List[int]:
        """
        Jednoduchá diatonická stupnica (major/minor) v 12-tónovom cykle.
        """
        if is_major:
            pattern = [0, 2, 4, 5, 7, 9, 11]
        else:
            pattern = [0, 2, 3, 5, 7, 8, 10]
        return [ (key_root + step) % 12 for step in pattern ]

    # ---------------------------------------------------------
    # HLAVNÁ FUNKCIA
    # ---------------------------------------------------------
    def analyze(
        self,
        pitches: List[int],
        key_root: Optional[int] = None,
        is_major: bool = True,
        chord_root: Optional[int] = None,
    ) -> Dict[int, str]:
        """
        Vstup:
            pitches   - zoznam MIDI pitch hodnôt (napr. [60, 64, 67])
            key_root  - root stupnice (0–11, C=0, C#=1, ...)
            is_major  - True = dur, False = mol
            chord_root- root akordu (0–11), ak je známy

        Výstup:
            dict: pitch -> HarmonyRole.*
        """
        roles: Dict[int, str] = {}

        # Ak nemáme key_root, nevieme posúdiť scale/outside → všetko berieme len voči akordu
        scale_pitches: List[int] = []
        if key_root is not None:
            scale_pitches = self._build_scale(key_root, is_major)

        for p in pitches:
            norm = self._normalize_pitch(p)

            # 1) ROOT akordu
            if chord_root is not None:
                interval = (norm - chord_root) % 12

                if interval in self.chord_intervals[HarmonyRole.ROOT]:
                    roles[p] = HarmonyRole.ROOT
                    continue

                # 2) CHORD TONES
                if interval in self.chord_intervals[HarmonyRole.CHORD_TONE]:
                    roles[p] = HarmonyRole.CHORD_TONE
                    continue

                # 3) TENSIONS
                if interval in self.chord_intervals[HarmonyRole.TENSION]:
                    roles[p] = HarmonyRole.TENSION
                    continue

            # 4) SCALE TONE vs OUTSIDE
            if scale_pitches:
                if norm in scale_pitches:
                    roles[p] = HarmonyRole.SCALE_TONE
                else:
                    roles[p] = HarmonyRole.OUTSIDE
            else:
                # Bez informácie o stupnici a akorde nevieme posúdiť → default
                roles[p] = HarmonyRole.OUTSIDE

        return roles

    # ---------------------------------------------------------
    # VYŠŠIA ÚROVEŇ – ANALÝZA Z NOTE OBJEKTOV
    # ---------------------------------------------------------
    def analyze_notes(
        self,
        notes: List[object],
        key_root: Optional[int] = None,
        is_major: bool = True,
        chord_root: Optional[int] = None,
        pitch_attr: str = "pitch",
    ) -> Dict[object, str]:
        """
        Alternatíva, ak pracuješ s objektmi nôt (napr. timeline items).

        notes      - zoznam objektov, ktoré majú atribút s názvom pitch_attr
        pitch_attr - názov atribútu, kde je uložený MIDI pitch (default 'pitch')

        Výstup:
            dict: note_obj -> HarmonyRole.*
        """
        pitches = []
        for n in notes:
            if hasattr(n, pitch_attr):
                pitches.append(getattr(n, pitch_attr))

        pitch_roles = self.analyze(
            pitches=pitches,
            key_root=key_root,
            is_major=is_major,
            chord_root=chord_root,
        )

        result: Dict[object, str] = {}
        for n in notes:
            if hasattr(n, pitch_attr):
                p = getattr(n, pitch_attr)
                result[n] = pitch_roles.get(p, HarmonyRole.OUTSIDE)
            else:
                result[n] = HarmonyRole.OUTSIDE

        return result
