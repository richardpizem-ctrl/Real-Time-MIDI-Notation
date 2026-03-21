# notation_engine/notation_renderer.py

from .layout_engine import PixelLayoutEngine


class NotationRenderer:
    def __init__(self, canvas=None):
        """
        Renderer zodpovedný za vykresľovanie nôt a akordov.
        - canvas: tkinter canvas, pygame surface alebo vlastný objekt
        """
        self.canvas = canvas
        self.last_drawn_chord = None  # aby sme nekreslili akord 100x za sekundu

        # 🔵 Pixelový layout engine – pridali sme ho sem
        self.pixel_layout = PixelLayoutEngine()

    def set_canvas(self, canvas):
        """
        Umožní dodatočne nastaviť canvas.
        """
        self.canvas = canvas

    # ---------------------------------------------------------
    # 1) VYKRESLENIE AKORDU
    # ---------------------------------------------------------
    def draw_chord(self, chord):
        """
        Vykreslí názov akordu nad notami.
        chord je objekt typu Chord alebo None.
        """

        if chord is None:
            return

        chord_name = chord.name

        # Ak nemáme canvas → vypíšeme do konzoly
        if self.canvas is None:
            if chord_name != self.last_drawn_chord:
                print(f"[Renderer] Current chord: {chord_name}")
                self.last_drawn_chord = chord_name
            return

        # Ak máme canvas → vykreslíme text
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
        """
        Vykreslí notu s farbou, ktorú vypočítal NotationEngine.
        Očakáva dict:
        {
            "pitch": int,
            "start": float,
            "duration": float,
            "color": "#RRGGBB",
            "x": float,
            "y": float
        }
        """

        if self.canvas is None:
            print(f"[Renderer] Note: pitch={note['pitch']}, color={note['color']}")
            return

        # 🔵 Používame x/y z PixelLayoutEngine
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
        """
        Vykreslí všetky noty + akord.
        """

        if self.canvas is None:
            print("[Renderer] Canvas nie je nastavený.")
            return

        # Najprv akord
        self.draw_chord(current_chord)

        # 🔵 PixelLayoutEngine → prepočet x/y
        positioned = self.pixel_layout.layout_timeline(timeline)

        # Potom noty
        for note in positioned:
            self.draw_note(note)
