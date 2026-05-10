# =========================================================
# TrackSelectionController v4.0.0
# Stable controller for managing the active MIDI track
# =========================================================

class TrackSelectionController:
    """
    TrackSelectionController (v4.0.0)
    ---------------------------------
    Minimal, stable controller for managing the active MIDI track.

    Used by:
        - TrackControlManager
        - UI (Track Switcher, Inspector)
        - Renderer (active track lookup)

    Features:
        - real‑time safe
        - no exceptions
        - fast clamping
        - clean English API
        - ready for v5 (multi‑track focus, AI assist)
    """

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)
        self.active_track = 0  # default active track (0-based)

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _clamp(self, track: int) -> int:
        """Clamp track index to the valid range 0–track_count-1."""
        try:
            t = int(track)
        except Exception:
            return 0
        return 0 if t < 0 else (self.track_count - 1 if t >= self.track_count else t)

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
