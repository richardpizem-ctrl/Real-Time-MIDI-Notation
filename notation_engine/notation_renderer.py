# notation_engine/notation_renderer.py

from .layout_engine import PixelLayoutEngine


class NotationRenderer:
    def __init__(self, canvas=None):
        """
        Renderer zodpovedný za vykresľovanie nôt a akordov.
        - canvas: tkinter canvas, pygame surface alebo vlastný objekt
        """
        self.canvas = canvas
        self.last_drawn_chord = None

        # Pixelový layout engine
        self.pixel_layout = PixelLayoutEngine()

    def set_canvas(self, canvas):
        self.canvas = canvas

    # ---------------------------------------------------------
    # 0) VYKRESLENIE OSNOVY (5 liniek)
    # ---------------------------------------------------------
    def draw_staff(self, y_top=80, spacing=12, width=2000):
        """
        Vykreslí 5 liniek notovej osnovy.
        y_top = horná linka
        spacing = vzdialenosť medzi linkami
        width = šírka osnovy
        """
        if self.canvas is None:
            return

        for i in range(5):
            y = y_top + i * spacing
            self.canvas.create_line(0, y, width, y, fill="#666666", width=2)

    # ---------------------------------------------------------
    # 0.1) BASOVÁ OSNOVA (ďalších 5 liniek)
    # ---------------------------------------------------------
    def draw_bass_staff(self, y_top=80 + 140, spacing=12, width=2000):
        """
        Vykreslí basovú osnovu (5 liniek pod hlavnou osnovou).
        """
        self.draw_staff(y_top=y_top, spacing=spacing, width=width)

    # ---------------------------------------------------------
    # 0.5) VYKRESLENIE TAKTOVEJ ČIARY
    # ---------------------------------------------------------
    def draw_barline(self, x, y_top=80, height=48 + 140):
        """
        Vykreslí taktovú čiaru cez obe osnovy.
        """
        if self.canvas is None:
            return

        self.canvas.create_line(x, y_top, x, y_top + height, fill="#AAAAAA", width=2)

    # ---------------------------------------------------------
    # 1) VYKRESLENIE AKORDU
    # ---------------------------------------------------------
    def draw_chord(self, chord):
        if chord is None:
            return

        chord_name = chord.name

        if self.canvas is None:
            if chord_name != self.last_drawn_chord:
                print(f"[Renderer] Current chord: {chord_name}")
                self.last_drawn_chord = chord_name
            return

        self.canvas.delete("chord_text")

        self.canvas.create_text(
            100, 30,
            text=chord_name,
            fill="#FFFFFF",
            font=("Arial", 20, "bold"),
            tags="chord_text"
        )

        self.last_drawn_chord = chord_name

    # ---------------------------------------------------------
    # 2) VYKRESLENIE NOTY
    # ---------------------------------------------------------
    def draw_note(self, note):
        if self.canvas is None:
            print(f"[Renderer] Note: pitch={note['pitch']}, color={note['color']}")
            return

        x = note["x"]
        y = note["y"]

        width = note["duration"] * 50
        height = 10

        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=note["color"],
            outline=""
        )

    # ---------------------------------------------------------
    # 3) VYKRESLENIE CELEJ TIMELINE
    # ---------------------------------------------------------
    def render(self, timeline, current_chord=None):
        if self.canvas is None:
            print("[Renderer] Canvas nie je nastavený.")
            return

        # 🔵 0) Hlavná osnova (melody)
        self.draw_staff(y_top=80)

        # 🔵 0.1) Basová osnova (bass)
        self.draw_bass_staff(y_top=80 + 140)

        # 🔵 0.5) Taktové čiary podľa LayoutEngine barline symbolov
        for note in timeline:
            if note.get("type") == "barline":
                x = note.get("start", 0) * 40
                self.draw_barline(x)

        # 🔵 1) Akord
        self.draw_chord(current_chord)

        # 🔵 2) PixelLayoutEngine → prepočet x/y
        positioned = self.pixel_layout.layout_timeline(timeline)

        # 🔵 3) Noty podľa stopy
        for note in positioned:
            self.draw_note(note)
