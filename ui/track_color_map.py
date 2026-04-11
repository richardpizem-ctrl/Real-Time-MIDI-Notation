class TrackColorMap:
    """
    Mapovanie farieb pre 16 MIDI stôp podľa Yamaha štandardu.
    UI aj Renderer používajú tieto farby na konzistentné zobrazenie.
    """

    def __init__(self):
        # Farby sú v hex formáte (#RRGGBB)
        self.colors = [
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
        ]

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def get_color(self, track: int) -> str:
        """
        Vráti farbu pre danú stopu (0–15).
        Ak index nie je platný, vráti fallback farbu.
        """
        try:
            if 0 <= track < len(self.colors):
                return self.colors[track]
        except Exception:
            pass

        return "#FFFFFF"  # fallback farba

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
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
