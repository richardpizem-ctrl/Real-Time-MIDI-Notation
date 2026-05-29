# =========================================================
# TrackSelectionController v4.3.0
# Ultra‑rýchly controller pre správu aktívnej MIDI stopy
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

class TrackSelectionController:
    """
    TrackSelectionController (v4.3.0)
    ---------------------------------
    Minimal, ultra‑rýchly controller pre správu aktívnej MIDI stopy.

    Používajú ho:
        - TrackControlManager
        - UI (Track Switcher, Inspector)
        - Renderer (active track lookup)

    Vylepšenia v4.3.0:
        - __slots__ pre ultra‑nízku latenciu
        - rýchlejší clamp
        - žiadne výnimky
        - čisté API
        - pripravené pre v5 (multi‑track focus, AI assist)
    """

    __slots__ = ("track_count", "active_track")

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)
        self.active_track = 0  # default active track (0-based)

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _clamp(self, track: int) -> int:
        """Clamp track index to the valid range 0–track_count-1 (ultra‑fast)."""
        try:
            t = int(track)
        except Exception:
            return 0

        if t < 0:
            return 0
        if t >= self.track_count:
            return self.track_count - 1
        return t

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def select(self, track: int):
        """Set the active track (0-based index)."""
        self.active_track = self._clamp(track)

    def get_active_track(self) -> int:
        """Return the currently active track index."""
        return self.active_track

    # ---------------------------------------------------------
    # NO-OP API (UIManager compatibility)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        """Alias for select() – used by UIManager."""
        self.select(track_index)
