# notation_engine/symbol_manager.py

class SymbolManager:
    """
    SymbolManager vytvára vizuálne a logické symboly pre noty.
    Zatiaľ jednoduché farby a rytmické názvy, ale pripravené
    na budúce rozšírenie (grafické symboly, SVG, fonty).
    """

    def __init__(self):
        # Farebná paleta podľa výšky tónu (12-TET)
        self.pitch_colors = {
            0: "#FF5555",   # C
            1: "#FF8855",   # C#
            2: "#FFCC55",   # D
            3: "#DDFF55",   # D#
            4: "#99FF55",   # E
            5: "#55FF88",   # F
            6: "#55FFCC",   # F#
            7: "#55DDFF",   # G
            8: "#5599FF",   # G#
            9: "#8855FF",   # A
            10: "#CC55FF",  # A#
            11: "#FF55CC",  # B
        }

    # ---------------------------------------------------------
    # HLAVNÁ METÓDA
    # ---------------------------------------------------------
    def get_symbol(self, note, rhythm: str):
        """
        Vráti symbol pre danú notu.
        - note: objekt Note z MidiNoteMapperu
        - rhythm: názov rytmickej hodnoty (quarter, eighth, ...)
        """

        if note is None or rhythm is None:
            return None

        pitch_class = note.pitch % 12
        color = self.pitch_colors.get(pitch_class, "#FFFFFF")

        symbol = {
            "pitch": note.pitch,
            "duration_ticks": note.duration.ticks,
            "rhythm": rhythm,
            "measure": note.position.measure,
            "beat": note.position.beat,
            "color": color,
            "label": f"{note.pitch}-{rhythm}"
        }

        return symbol
