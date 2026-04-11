class TrackSelectionController:
    """
    Controller pre správu aktívnej MIDI stopy.
    UI volá select(track), renderer si stav iba číta.
    """

    def __init__(self, track_count: int = 16):
        self.track_count = track_count
        self.active_track = 0  # predvolená aktívna stopa

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _clamp(self, track: int) -> int:
        """Zabezpečí, že index je v rozsahu 0–track_count-1."""
        try:
            t = int(track)
        except Exception:
            return 0
        return max(0, min(self.track_count - 1, t))

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def select(self, track: int):
        """Nastaví aktívnu stopu, ak je v rozsahu."""
        self.active_track = self._clamp(track)

    def get_active_track(self) -> int:
        """Vráti index aktuálne aktívnej stopy."""
        return self.active_track

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        """Alias pre select() – UIManager volá túto metódu."""
        self.select(track_index)
