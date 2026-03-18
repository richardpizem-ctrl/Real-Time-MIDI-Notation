class SymbolManager:
    def __init__(self):
        # Tu môžeme neskôr načítať grafické symboly alebo fonty
        pass

    def get_symbol(self, note_name, rhythm_info):
        """
        Vráti symbol pre danú notu a rytmickú hodnotu.
        Zatiaľ len jednoduchá textová reprezentácia.
        """
        if note_name is None or rhythm_info is None:
            return None

        # Príklad symbolu: "C4-quarter"
        return f"{note_name}-{rhythm_info}"

