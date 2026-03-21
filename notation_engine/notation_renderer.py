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

        # Farby pre jednotlivé stopy
        self.track_colors = {
            "melody": "#4DA6FF",   # modrá
            "bass": "#66CC66",     # zelená
            "drums": "#FF9933",    # oranžová
            "chords": "#FFFFFF"
        }

    def set_canvas(self, canvas):
        self.canvas = canvas

    # ---------------------------------------------------------
    # 0) VYKRESLENIE OSNOVY (5 liniek)
    # ---------------------------------------------------------
    def draw_staff(self, y_top=80, spacing=12, width=2000):
        if self.canvas is None:
            return

        for i in range(5):
            y = y_top + i * spacing
            self.canvas.create_line(0, y, width, y, fill="#666666", width=2)

    # ---------------------------------------------------------
    # 0.1) BASOVÁ OSNOVA (ďalších 5 liniek)
    # ---------------------------------------------------------
    def draw_bass_staff(self, y_top=80 + 140, spacing=12, width=2000):
        self.draw_staff(y_top=y_top, spacing=spacing, width=width)

    # ---------------------------------------------------------
    # 0.2) NÁZVY STÔP NAĽAVO
    # ---------------------------------------------------------
    def draw_track_labels(self):
        """
        Vykreslí názvy stôp naľavo od osnov.
        """
        if self.canvas is None:
            return

        # Melody – pri hornej osnove
        self.canvas.create_text(
            40, 80 + 24,
            text="Melody",
            fill="#4DA6FF",
            font=("Arial", 12, "bold"),
            anchor="e"
        )

        # Bass – pri basovej osnove
        self.canvas.create_text(
            40, 80 + 140 + 24,
            text="Bass",
            fill="#66CC66",
            font=("Arial", 12, "bold"),
            anchor="e"
        )

        # Drums – pod basovou osnovou (orientačne)
        self.canvas.create_text(
            40, 80 + 140 + 80,
            text="Drums",
            fill="#FF9933",
            font=("Arial", 12, "bold"),
            anchor="e"
        )

    # ---------------------------------------------------------
    # 0.5) VYKRESLENIE TAKTOVEJ ČIARY
    # ---------------------------------------------------------
    def draw_barline(self, x, y_top=80, height=48 + 140):
        if self.canvas is None:
            return

        self.canvas.create_line(x, y_top, x, y_top + height, fill="#AAAAAA", width=2)

    # ---------------------------------------------------------
    # 0.6) AKORD NAD TAKTOM
    # ---------------------------------------------------------
    def draw_chord_above_bar(self, chord_name, x):
        if self.canvas is None:
            return

        self.canvas.create_text(
            x + 10, 50,
            text=chord_name,
            fill="#FFFFAA",
            font=("Arial", 14, "bold")
        )

    # ---------------------------------------------------------
    # 1) VYKRESLENIE HLAVNÉHO AKORDU
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
    # 2) RYTMICKÉ SYMBOLY
    # ---------------------------------------------------------
    def draw_rhythm_symbol(self, x, y, duration):
        """
        duration:
            1.0 = celá
            0.5 = polová
            0.25 = štvrťová
            0.125 = osminová
        """
        if self.canvas is None:
            return

        if duration >= 1.0:
            symbol = "𝅝"   # whole
        elif duration >= 0.5:
            symbol = "𝅗𝅥"   # half
        elif duration >= 0.25:
            symbol = "♩"   # quarter
        else:
            symbol = "♪"   # eighth

        self.canvas.create_text(
            x - 10, y - 15,
            text=symbol,
            fill="#FFFFFF",
            font=("Arial", 14)
        )

    # ---------------------------------------------------------
    # 3) VYKRESLENIE NOTY (melody, bass, drums)
    # ---------------------------------------------------------
    def draw_note(self, note):
        if self.canvas is None:
            print(f"[Renderer] Note: pitch={note['pitch']}, color={note['color']}")
            return

        x = note["x"]
        y = note["y"]

        width = note["duration"] * 50
        height = 10

        # Farba podľa stopy
        track = note.get("track_type", "melody")
        color = self.track_colors.get(track, "#FFFFFF")

        # Špeciálne pozície pre bubny
        if track == "drums":
            height = 6
            y += 20

        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=color,
            outline=""
        )

        # Rytmický symbol
        self.draw_rhythm_symbol(x, y, note["duration"])

    # ---------------------------------------------------------
    # 4) VYKRESLENIE CELEJ TIMELINE
    # ---------------------------------------------------------
    def render(self, timeline, current_chord=None):
        if self.canvas is None:
            print("[Renderer] Canvas nie je nastavený.")
            return

        # 🔵 0) Hlavná osnova (melody)
        self.draw_staff(y_top=80)

        # 🔵 0.1) Basová osnova (bass)
        self.draw_bass_staff(y_top=80 + 140)

        # 🔵 0.2) Názvy stôp naľavo
        self.draw_track_labels()

        # 🔵 0.5) Taktové čiary + akordy nad taktmi
        for note in timeline:
            if note.get("type") == "barline":
                x = note.get("start", 0) * 40
                self.draw_barline(x)

                if "chord" in note:
                    self.draw_chord_above_bar(note["chord"], x)

        # 🔵 1) Hlavný akord
        self.draw_chord(current_chord)

        # 🔵 2) PixelLayoutEngine → prepočet x/y
        positioned = self.pixel_layout.layout_timeline(timeline)

        # 🔵 3) Noty podľa stopy
        for note in positioned:
            self.draw_note(note)
