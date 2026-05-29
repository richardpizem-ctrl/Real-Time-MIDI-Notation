# =========================================================
# TrackColorMap v4.3.0
# Ultra‑rýchle mapovanie farieb pre 16 MIDI stôp (Yamaha štandard)
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

class TrackColorMap:
    """
    TrackColorMap (v4.3.0)
    ----------------------
    Poskytuje konzistentné farby pre 16 MIDI stôp podľa Yamaha štandardu.

    Vylepšenia v4.3.0:
        - __slots__ pre ultra‑nízku latenciu
        - okamžitý HEX aj RGB lookup (O(1))
        - predpočítané RGB tuple (žiadne runtime konverzie)
        - bezpečné fallback farby
        - drop‑in kompatibilita s UIManager 4.3.0
        - pripravené pre AI/TIMELINE color assist v5
    """

    __slots__ = (
        "colors_hex",
        "colors_rgb",
        "fallback_hex",
        "fallback_rgb",
    )

    def __init__(self):
        # HEX farby (nemenné)
        self.colors_hex = (
            "#FF4B4B",  # 0 - Red
            "#FF8A33",  # 1 - Orange
            "#FFC233",  # 2 - Yellow
            "#F2FF33",  # 3 - Lime
            "#A6FF33",  # 4 - Light Green
            "#33FF57",  # 5 - Green
            "#33FFBD",  # 6 - Aqua
            "#33E3FF",  # 7 - Light Blue
            "#3396FF",  # 8 - Blue
            "#335BFF",  # 9 - Deep Blue
            "#6A33FF",  # 10 - Violet
            "#A833FF",  # 11 - Purple
            "#E633FF",  # 12 - Magenta
            "#FF33C4",  # 13 - Pink
            "#FF337A",  # 14 - Rose
            "#FF334B",  # 15 - Red-Pink
        )

        # Predpočítané RGB tuple (nemenné, ultra‑rýchle)
        self.colors_rgb = tuple(self._hex_to_rgb(h) for h in self.colors_hex)

        # fallback
        self.fallback_hex = "#FFFFFF"
        self.fallback_rgb = (255, 255, 255)

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _hex_to_rgb(self, h: str):
        """Konverzia HEX → RGB tuple (real‑time safe)."""
        try:
            h = h.lstrip("#")
            return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))
        except Exception:
            return self.fallback_rgb

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def get_color(self, track: int) -> str:
        """
        Vráti farbu v HEX formáte (#RRGGBB).
        O(1), real‑time safe.
        """
        try:
            idx = int(track)
        except Exception:
            return self.fallback_hex

        if 0 <= idx < 16:
            return self.colors_hex[idx]

        return self.fallback_hex

    def get_color_rgb(self, track: int):
        """
        Vráti farbu v RGB formáte (r, g, b).
        O(1), real‑time safe.
        """
        try:
            idx = int(track)
        except Exception:
            return self.fallback_rgb

        if 0 <= idx < 16:
            return self.colors_rgb[idx]

        return self.fallback_rgb

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
