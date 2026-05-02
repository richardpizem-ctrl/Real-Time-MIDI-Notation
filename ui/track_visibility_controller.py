# =========================================================
# TrackVisibilityController v2.0.0
# Stabilný controller pre viditeľnosť MIDI stôp
# =========================================================

class TrackVisibilityController:
    """
    TrackVisibilityController (v2.0.0)
    ----------------------------------
    Správa viditeľnosti stôp.

    Používajú ho:
        - TrackControlManager
        - Renderer (na filtrovanie stôp)
        - UI (Inspector, Track Switcher, Track Selector)

    Vlastnosti:
        - real‑time safe
        - žiadne výnimky
        - rýchle boolean pole
        - jednotné API
    """

    def __init__(self, track_count: int = 16):
        self.track_count = int(track_count)
        # True = viditeľná, False = skrytá
        self._visible = [True] * self.track_count

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
    def is_visible(self, track: int) -> bool:
        """Vráti, či je daná stopa viditeľná."""
        t = self._clamp(track)
        try:
            return bool(self._visible[t])
        except Exception:
            return True

    def show(self, track: int):
        """Nastaví stopu ako viditeľnú."""
        t = self._clamp(track)
        try:
            self._visible[t] = True
        except Exception:
            pass

    def hide(self, track: int):
        """Nastaví stopu ako skrytú."""
        t = self._clamp(track)
        try:
            self._visible[t] = False
        except Exception:
            pass

    def toggle(self, track: int):
        """Prepne viditeľnosť danej stopy."""
        t = self._clamp(track)
        try:
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
    # NO-OP API (pre UIManager kompatibilitu)
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
