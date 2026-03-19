# notation_engine/notation_renderer.py

class NotationRenderer:
    def __init__(self, canvas=None):
        """
        Renderer zodpovedný za vykresľovanie nôt.
        - canvas: môže byť tkinter canvas, pygame surface, alebo vlastný objekt
        """
        self.canvas = canvas

    def set_canvas(self, canvas):
        """
        Umožní dodatočne nastaviť canvas.
        """
        self.canvas = canvas

    def draw_note(self, note):
        """
        Vykreslí notu s farbou, ktorú už vypočítal NotationEngine.
        Očakáva dict vo formáte:
        {
            "pitch": int,
            "start": float,
            "duration": float,
            "color": "#RRGGBB"
        }
        """

        if self.canvas is None:
            print(f"[Renderer] Note: pitch={note['pitch']}, color={note['color']}")
            return

        # --- Jednoduché grafické vykreslenie (placeholder) ---
        # X = čas (start)
        # Y = výška tónu (pitch)
        x = note["start"] * 50
        y = 400 - (note["pitch"] * 3)

        width = note["duration"] * 50
        height = 10

        # Vykreslenie farebného obdĺžnika
        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=note["color"],
            outline=""
        )

    def render(self, timeline):
        """
        Vykreslí celú časovú os.
        """
        if self.canvas is None:
            print("[Renderer] Canvas nie je nastavený.")
            return

        for note in timeline:
            self.draw_note(note)

