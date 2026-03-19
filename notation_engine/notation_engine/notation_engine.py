class NotationEngine:
    """
    Jednoduchý „mozog“ systému:
    - prijíma hotové noty zo StreamHandleru
    - ukladá ich do timeline
    - počíta takty a beaty podľa tempa a metra
    - voliteľne ich posiela rendereru
    """

    def __init__(self, renderer=None, tempo=120, time_signature=(4, 4)):
        # Renderer (napr. NotationRenderer) – môže byť None
        self.renderer = renderer

        # Uložené noty v timeline
        self.notes = []

        # Základné metrum
        self.tempo = tempo                  # BPM
        self.time_signature = time_signature  # (beats_per_bar, beat_unit)

        # Interný stav
        self.current_bar = 1
        self.current_beat = 0.0

    def set_renderer(self, renderer):
        """Dodatočne nastaví renderer, ak nebol daný v __init__."""
        self.renderer = renderer

    def add_note(self, note):
        """
        Očakáva dict z MidiNoteMapperu, napr:
        {
            'pitch': ...,
            'duration': ... (v sekundách),
            'channel': ...,
            'start_time': ...,
        }
        """
        # Výpočet dĺžky v beatoch podľa tempa
        seconds_per_beat = 60.0 / self.tempo
        duration_seconds = note.get("duration", 0.0)
        note_beats = duration_seconds / seconds_per_beat if seconds_per_beat > 0 else 0.0

        # Pridáme informáciu o takte a beate
        note_info = dict(note)
        note_info["bar"] = self.current_bar
        note_info["beat"] = self.current_beat

        # Uložíme do timeline
        self.notes.append(note_info)

        # Posunieme interný beat counter
        beats_per_bar = self.time_signature[0]
        self.current_beat += note_beats

        while self.current_beat >= beats_per_bar:
            self.current_beat -= beats_per_bar
            self.current_bar += 1

        # Pošleme do rendereru, ak existuje
        if self.renderer is not None:
            self.renderer.add_note(note_info)

    def get_timeline(self):
        """Vráti všetky noty v timeline."""
        return self.notes
