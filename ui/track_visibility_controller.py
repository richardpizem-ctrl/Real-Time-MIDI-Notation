class TrackVisibilityController:
    """
    Controller pre správu viditeľnosti 16 MIDI stôp.
    Každá stopa môže byť zapnutá alebo vypnutá.
    Renderer si tento stav iba číta.
    """

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)
        self.visibility = [True] * self.track_count  # True = stopa je viditeľná

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
    def show(self, track: int):
        """Zapne viditeľnosť danej stopy."""
        self.visibility[self._clamp(track)] = True

    def hide(self, track: int):
        """Vypne viditeľnosť danej stopy."""
        self.visibility[self._clamp(track)] = False

    def toggle(self, track: int):
        """Prepne viditeľnosť danej stopy."""
        t = self._clamp(track)
        self.visibility[t] = not self.visibility[t]

    def set_visible(self, track: int, visible: bool):
        """Explicitne nastaví viditeľnosť (pre kompatibilitu s UI/Manager)."""
        self.visibility[self._clamp(track)] = bool(visible)

    def is_visible(self, track: int) -> bool:
        """Vráti True/False podľa toho, či je stopa viditeľná."""
        return self.visibility[self._clamp(track)]
