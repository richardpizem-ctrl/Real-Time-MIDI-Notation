class NotationRenderer:
    """
    Jednoduchý textový renderer.
    Zobrazuje noty v konzole vždy, keď príde nová nota.
    Teraz podporuje aj bubnové značky.
    """

    def __init__(self):
        self.notes = []

        try:
            import pygame
            self.clock = pygame.time.Clock()
        except ImportError:
            self.clock = None

    def add_note(self, note):
        """Pridá hotovú notu do renderovacieho bufferu a vypíše ich."""
        self.notes.append(note)
        self.render()

    def render(self):
        """Textová vizualizácia nôt vrátane bubnových značiek."""
        print("\n--- RENDER ---")

        for n in self.notes:

            # základné info
            base = (
                f"pitch={n['pitch']}  dur={n['duration']}  "
                f"ch={n['channel']}  bar={n.get('bar')}  beat={n.get('beat')}"
            )

            # bubnové info (ak existuje)
            drum_info = ""
            if "drum" in n:
                d = n["drum"]
                drum_info = (
                    f"   [DRUM: {d['name']}, head={d['notehead_type']}, "
                    f"stem={d['stem_direction']}, "
                    f"open={d['is_open_hat']}, closed={d['is_closed_hat']}, "
                    f"ghost={d['is_ghost']}, accent={d['is_accent']}]"
                )

            # layering (ak existuje)
            layer = ""
            if "drum_layer_offset" in n:
                layer = f"   layer_offset={n['drum_layer_offset']}"

            print(base + drum_info + layer)

        print("--------------\n")

        if self.clock:
            self.clock.tick(60)
