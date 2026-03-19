# notation_engine/color_mapper.py

from typing import List, Optional
from notation_engine.chord_detector import Chord


# Definícia farieb (môžeš si ich neskôr zmeniť)
COLORS = {
    "chord": "#00A2FF",      # tóny akordu – modrá
    "scale": "#00FF7F",      # tóny stupnice – zelená
    "outside": "#FF4C4C",    # mimo stupnice – červená
    "bass": "#FFD700",       # basová stopa – zlatá
    "drums": "#FFFFFF",      # bicie – biela
}


def get_note_color(note: int,
                   chord: Optional[Chord],
                   scale: Optional[List[int]] = None,
                   track_type: str = "melody") -> str:
    """
    Vráti farbu pre danú MIDI notu podľa:
    - akordu
    - stupnice
    - typu stopy (melody, bass, drums)
    """

    # 1. Špeciálne farby pre basu a bicie
    if track_type == "bass":
        return COLORS["bass"]

    if track_type == "drums":
        return COLORS["drums"]

    # 2. Normalizácia MIDI noty (0–11)
    normalized = note % 12

    # 3. Akordové tóny majú najvyššiu prioritu
    if chord and normalized in chord.notes:
        return COLORS["chord"]

    # 4. Tóny stupnice (ak je definovaná)
    if scale and normalized in scale:
        return COLORS["scale"]

    # 5. Tóny mimo stupnice
    return COLORS["outside"]
