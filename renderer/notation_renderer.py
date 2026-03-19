class NotationRenderer:
    """
    Jednoduchý textový renderer.
    Zobrazuje noty v konzole vždy, keď príde nová nota.
    """

    def __init__(self):
        # tu budú všetky noty, ktoré prídu zo stream handlera
        self.notes = []

    def add_note(self, note):
        """Pridá hotovú notu do renderovacieho bufferu a vypíše ich."""
        self.notes.append(note)
        self.render()

    def render(self):
        """Zatiaľ len vypíše všetky noty. Neskôr tu môže byť textová notácia."""
        print("\n--- RENDER ---")
        for n in self.notes:
            print(
                f"{n['pitch']}  dur={n['duration']}  "
                f"ch={n['channel']}  bar={n.get('bar')}  beat={n.get('beat')}"
            )
        print("--------------\n")

      
