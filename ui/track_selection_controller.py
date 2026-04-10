class TrackSelectionController:
    """
    Controller pre správu aktívnej MIDI stopy.
    UI volá select(track), renderer si stav iba číta.
    """

    def __init__(self, track_count: int = 16):
        # Predvolená aktívna stopa je 0 (Track 1)
        self.track_count = track_count
        self.active_track = 0

    def select(self, track: int):
        """Nastaví aktívnu stopu, ak je v rozsahu."""
        if 0 <= track < self.track_count:
            self.active_track = track

    def get_active_track(self) -> int:
        """Vráti index aktuálne aktívnej stopy."""
        return self.active_track
