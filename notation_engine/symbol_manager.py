# =========================================================
# SymbolManager v2.0.0
# Stabilný generátor vizuálnych/logických symbolov pre noty
# =========================================================

class SymbolManager:
    """
    SymbolManager (v2.0.0):
    - bezpečné spracovanie Note objektov
    - fallback hodnoty pri chybách
    - farebná paleta podľa pitch-class (12-TET)
    """

    def __init__(self):
        self.pitch_colors = {
            0:  "#FF5555",   # C
            1:  "#FF8855",   # C#
            2:  "#FFCC55",   # D
            3:  "#DDFF55",   # D#
            4:  "#99FF55",   # E
            5:  "#55FF88",   # F
            6:  "#55FFCC",   # F#
            7:  "#55DDFF",   # G
            8:  "#5599FF",   # G#
            9:  "#8855FF",   # A
            10: "#CC55FF",   # A#
            11: "#FF55CC",   # B
        }

    # ---------------------------------------------------------
    # HLAVNÁ METÓDA
    # ---------------------------------------------------------
    def get_symbol(self, note, rhythm: str):
        """
        Vráti symbol pre danú notu.

        Stabilizované (v2.0.0):
        - ochrana pred None
        - ochrana pred nevalidnými typmi
        - bezpečné čítanie pitch/duration/position
        - fallback farby a labelu
        """

        # -----------------------------
        # VALIDÁCIA VSTUPU
        # -----------------------------
        if note is None or rhythm is None:
            return {
                "pitch": 60,
                "duration_ticks": 0,
                "rhythm": "unknown",
                "measure": 0,
                "beat": 1.0,
                "color": "#FFFFFF",
                "label": "invalid-note",
            }

        # -----------------------------
        # PITCH
        # -----------------------------
        try:
            pitch = int(note.pitch)
        except Exception:
            pitch = 60

        try:
            pitch_class = pitch % 12
        except Exception:
            pitch_class = 0

        color = self.pitch_colors.get(pitch_class, "#FFFFFF")

        # -----------------------------
        # DURATION
        # -----------------------------
        try:
            duration_ticks = int(note.duration.ticks)
        except Exception:
            duration_ticks = 0

        # -----------------------------
        # POSITION
        # -----------------------------
        try:
            measure = int(note.position.measure)
        except Exception:
            measure = 0

        try:
            beat = float(note.position.beat)
        except Exception:
            beat = 1.0

        # -----------------------------
        # SYMBOL OUTPUT
        # -----------------------------
        return {
            "pitch": pitch,
            "duration_ticks": duration_ticks,
            "rhythm": rhythm,
            "measure": measure,
            "beat": beat,
            "color": color,
            "label": f"{pitch}-{rhythm}",
        }
