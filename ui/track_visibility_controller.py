# =========================================================
# TrackVisibilityController v4.0.0
# Stabilný controller pre viditeľnosť MIDI stôp
# =========================================================

class TrackVisibilityController:
    """
    TrackVisibilityController (v4.0.0)
    ----------------------------------
    Správa viditeľnosti stôp.

    Vylepšenia v4:
        - rýchlejší boolean lookup
        - bezpečné volania (žiadne výnimky)
        - okamžitý clamp
        - drop‑in kompatibilita
        - pripravené pre v5 (dynamic track allocation)
    """

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)
        self._visible = [True] * self.track_count  # True = viditeľná

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _clamp(self, track: int) -> int:
        """Zabezpečí, že index je v rozsahu 0–track_count-1."""
        try:
            t = int(track)
        except Exception:
            return 0
        return 0 if t < 0 else (self.track_count - 1 if t >= self.track_count else t)

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def is_visible(self, track: int) -> bool:
        """Vráti, či je daná stopa viditeľná."""
        try:
            return self._visible[self._clamp(track)]
        except Exception:
            return True

    def show(self, track: int):
        """Nastaví stopu ako viditeľnú."""
        try:
            self._visible[self._clamp(track)] = True
        except Exception:
            pass

    def hide(self, track: int):
        """Nastaví stopu ako skrytú."""
        try:
            self._visible[self._clamp(track)] = False
        except Exception:
            pass

    def toggle(self, track: int):
        """Prepne viditeľnosť danej stopy."""
        try:
            t = self._clamp(track)
            self._visible[t] = not self._visible[t]
        except Exception:
            pass

    def show_all(self):
        """Zobrazí všetky stopy."""
        for i in range(self.track_count):
            self._visible[i] = True

    def hide_all(self):
        """Skryje všetky stopy."""
        for i in range(self.track_count):
            self._visible[i] = False

    # ---------------------------------------------------------
    # NO-OP API (UIManager kompatibilita)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        """Alias – UI môže volať priamo, ale stav držíme interne."""
        if visible:
            self.show(track_index)
        else:
            self.hide(track_index)

    def set_active_track(self, track_index: int):
        """Viditeľnosť nerieši aktívnu stopu – no-op."""
        return
