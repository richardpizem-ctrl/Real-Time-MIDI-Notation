class TrackVisibilityController:
    """
    Controller pre správu viditeľnosti 16 MIDI stôp.
    Každá stopa môže byť zapnutá alebo vypnutá.
    Renderer si tento stav iba číta.
    """

    def __init__(self, track_count: int = 16):
        # True = stopa je viditeľná
        # False = stopa je skrytá
        self.visibility = [True] * track_count

    def show(self, track: int):
        """Zapne viditeľnosť danej stopy."""
        self.visibility[track] = True

    def hide(self, track: int):
        """Vypne viditeľnosť danej stopy."""
        self.visibility[track] = False

    def toggle(self, track: int):
        """Prepne viditeľnosť danej stopy."""
        self.visibility[track] = not self.visibility[track]

    def is_visible(self, track: int) -> bool:
        """Vráti True/False podľa toho, či je stopa viditeľná."""
        return self.visibility[track]
