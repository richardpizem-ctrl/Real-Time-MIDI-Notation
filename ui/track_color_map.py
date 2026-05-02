# =========================================================
# TrackColorMap v2.0.0
# Stabilné mapovanie farieb pre 16 MIDI stôp (Yamaha štandard)
# =========================================================

class TrackColorMap:
    """
    TrackColorMap (v2.0.0)
    ----------------------
    Poskytuje konzistentné farby pre 16 MIDI stôp podľa Yamaha štandardu.
    Používa sa v:
        - UI (PianoUI, PianoRollUI, StaffUI, TimelineUI)
        - Renderer (GraphicNotationRenderer)
        - MIDI pipeline (track routing)

    Vlastnosti:
        - tuple = nemenné, rýchle, bezpečné
        - real‑time safe
        - fallback farba pri nevalidnom indexe
        - kompatibilné s UIManager API (no‑op metódy)
        - pripravené na v3 (AI/TIMELINE color assist)
    """

    def __init__(self):
        # Farby v hex formáte (#RRGGBB)
        self.colors = (
            "#FF4B4B",  # Track 1 - Red
            "#FF8A33",  # Track 2 - Orange
            "#FFC233",  # Track 3 - Yellow
            "#F2FF33",  # Track 4 - Lime
            "#A6FF33",  # Track 5 - Light Green
            "#33FF57",  # Track 6 - Green
            "#33FFBD",  # Track 7 - Aqua
            "#33E3FF",  # Track 8 - Light Blue
            "#3396FF",  # Track 9 - Blue
            "#335BFF",  # Track 10 - Deep Blue
            "#6A33FF",  # Track 11 - Violet
            "#A833FF",  # Track 12 - Purple
            "#E633FF",  # Track 13 - Magenta
            "#FF33C4",  # Track 14 - Pink
            "#FF337A",  # Track 15 - Rose
            "#FF334B",  # Track 16 - Red-Pink
        )

        self.fallback = "#FFFFFF"

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def get_color(self, track: int) -> str:
        """
        Vráti farbu pre danú stopu (0–15).
        Ak index nie je platný, vráti fallback farbu.
        """
        try:
            idx = int(track)
        except Exception:
            return self.fallback

        if 0 <= idx < len(self.colors):
            return self.colors[idx]

        return self.fallback

    # ---------------------------------------------------------
    # NO-OP API (UIManager kompatibilita)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        """TrackColorMap farby nemení – bezpečný no-op."""
        return

    def update_visibility(self, track_index: int, visible: bool):
        """TrackColorMap nerieši viditeľnosť – bezpečný no-op."""
        return

    def set_active_track(self, track_index: int):
        """TrackColorMap nerieši aktívnu stopu – bezpečný no-op."""
        return
