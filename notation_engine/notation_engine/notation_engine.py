# notation_engine/notation_engine.py

from notation_engine.color_mapper import get_note_color


class NotationEngine:
    def __init__(self):
        # Zoznam všetkých nôt v časovej osi
        self.timeline = []

        # Aktuálny akord (nastavuje stream_handler)
        self.current_chord = None

        # Renderer (nastaví sa cez set_renderer)
        self.renderer = None

    def set_renderer(self, renderer):
        """
        Prepojenie s grafickým rendererom.
        Renderer musí mať metódu draw_note().
        """
        self.renderer = renderer

    def set_current_chord(self, chord):
        """
        StreamHandler sem posiela aktuálny akord.
        """
        self.current_chord = chord

    def add_note(self, note):
        """
        Pridá notu do časovej osi a zafarbí ju podľa akordu.
        Očakáva dict vo formáte:
        {
            "pitch": int,
            "start": float,
            "duration": float
        }
        """

        # 1. Získame farbu pre danú notu
        color = get_note_color(
            note=note["pitch"],
            chord=self.current_chord,
            scale=None,            # stupnicu doplníme neskôr
            track_type="melody"    # neskôr môžeme meniť podľa stopy
        )

        # 2. Pridáme farbu do objektu noty
        note["color"] = color

        # 3. Uložíme notu do timeline
        self.timeline.append(note)

        # 4. Ak máme renderer, vykreslíme notu
        if self.renderer:
            self.renderer.draw_note(note)

    def get_timeline(self):
        """
        Vráti všetky noty v časovej osi.
        """
        return self.timeline

  
        
