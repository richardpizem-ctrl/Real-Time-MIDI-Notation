class NotationRenderer:
    """
    Jednoduchý textový renderer.
    Zobrazuje noty v konzole vždy, keď príde nová nota.
    Podporuje aj bubnové značky a layering.
    """

    def __init__(self):
        self.notes = []

        # pygame clock je voliteľný (len ak je pygame dostupný)
        try:
            import pygame
            self.clock = pygame.time.Clock()
        except Exception:
            self.clock = None

    # ---------------------------------------------------------
    # API – pridanie noty
    # ---------------------------------------------------------
    def add_note(self, note):
        """
        Pridá hotovú notu do renderovacieho bufferu a vypíše ju.
        Očakáva dict s kľúčmi:
        - pitch
        - duration
        - channel
        - bar
        - beat
        - drum (voliteľné)
        - drum_layer_offset (voliteľné)
        """
        if not isinstance(note, dict):
            print("⚠️ NotationRenderer.add_note: neplatný objekt:", note)
            return

        try:
            self.notes.append(note.copy())
        except Exception:
            print("⚠️ NotationRenderer.add_note: chyba pri kopírovaní objektu")
            return

        self.render()

    # ---------------------------------------------------------
    # Textový výpis
    # ---------------------------------------------------------
    def render(self):
        """Textová vizualizácia nôt vrátane bubnových značiek."""
        print("\n--- RENDER ---")

        for n in self.notes:
            try:
                base = (
                    f"pitch={n.get('pitch')}  "
                    f"dur={n.get('duration')}  "
                    f"ch={n.get('channel')}  "
                    f"bar={n.get('bar')}  "
                    f"beat={n.get('beat')}"
                )
            except Exception:
                base = "[NEPLATNÁ NOTA]"

            drum_info = ""
            try:
                if "drum" in n and isinstance(n["drum"], dict):
                    d = n["drum"]
                    drum_info = (
                        f"   [DRUM: {d.get('name')}, "
                        f"head={d.get('notehead_type')}, "
                        f"stem={d.get('stem_direction')}, "
                        f"open={d.get('is_open_hat')}, "
                        f"closed={d.get('is_closed_hat')}, "
                        f"ghost={d.get('is_ghost')}, "
                        f"accent={d.get('is_accent')}]"
                    )
            except Exception:
                drum_info = "   [DRUM: ERROR]"

            layer = ""
            try:
                if "drum_layer_offset" in n:
                    layer = f"   layer_offset={n['drum_layer_offset']}"
            except Exception:
                layer = ""

            print(base + drum_info + layer)

        print("--------------\n")

        # FPS limit (ak pygame existuje)
        try:
            if self.clock:
                self.clock.tick(60)
        except Exception:
            pass
