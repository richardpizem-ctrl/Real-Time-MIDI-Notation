class NotationRenderer:
    def __init__(self):
        # Tu môžeme neskôr pridať grafické vykresľovanie
        pass

    def render(self, symbol):
        """
        Jednoduché vykreslenie symbolu.
        Zatiaľ len vypíše symbol do konzoly.
        """
        if symbol is None:
            return

        print(f"Rendered symbol: {symbol}")
Add basic notation renderer

