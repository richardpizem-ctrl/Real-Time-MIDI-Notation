class NotationRenderer:
    def __init__(self):
        # tu budú všetky noty, ktoré prídu zo stream handlera
        self.notes = []

    def add_note(self, note):
        """Pridá hotovú notu do renderovacieho bufferu."""
        self.notes.append(note)
        self.render()

    def render(self):
        """Zatiaľ len vypíše všetky noty. Neskôr tu bude grafika."""
        print("\n--- RENDER ---")
        for n in self.notes:
            print(f"{n['pitch']}  dur={n['duration']}  ch={n['channel']}  beat={n['beat']}")
        print("--------------\n")
