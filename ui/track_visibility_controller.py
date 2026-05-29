# =========================================================
# TrackVisibilityController v4.3.0
# Ultra‑rýchly controller pre viditeľnosť MIDI stôp
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

class TrackVisibilityController:
    """
    TrackVisibilityController (v4.3.0)
    ----------------------------------
    Správa viditeľnosti stôp.

    Vylepšenia v4.3.0:
        - __slots__ pre ultra‑nízku latenciu
        - rýchlejší boolean lookup
        - okamžitý clamp (bez vetvenia navyše)
        - real‑time safe (žiadne výnimky)
        - pripravené pre v5 (dynamic track allocation)
        - drop‑in kompatibilita s UIManager a TrackControlManager
    """

    __slots__ = ("track_count", "_visible")

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)
        self._visible = [True] * self.track_count  # True = viditeľná

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------
    def _clamp(self, track: int) -> int:
        """Clamp index to 0–track_count-1 (ultra‑fast, no exceptions)."""
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
    def is_visible(self, track: int) -> bool:
        """Vráti, či je daná stopa viditeľná (real‑time safe)."""
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
        """Zobrazí všetky stopy (O(n), žiadne výnimky)."""
        vis = self._visible
        for i in range(self.track_count):
            vis[i] = True

    def hide_all(self):
        """Skryje všetky stopy (O(n), žiadne výnimky)."""
        vis = self._visible
        for i in range(self.track_count):
            vis[i] = False

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
