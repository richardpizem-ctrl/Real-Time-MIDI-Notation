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

        # Buffer pre noty a akordy
        self.buffer = []

        # Farby pre jednotlivé stopy
        self.track_colors = {
            "melody": "#4DA6FF",
            "bass": "#66CC66",
            "drums": "#FF9933",
            "chords": "#FFFFFF"
        }

        # Font pre akordy (ak je canvas tkinter)
        self.chord_font = ("Arial", 16, "bold")

        # posledná vykreslená tónina
        self.last_key = None

    def set_canvas(self, canvas):
        self.canvas = canvas

    # ---------------------------------------------------------
    # ADD NOTE
    # ---------------------------------------------------------
    def add_note(self, note_dict):
        positioned = self.pixel_layout.layout_single(note_dict)
        self.buffer.append(positioned)

        if self.canvas:
            self.draw_note(positioned)
        else:
            print(f"[Renderer] Note: pitch={positioned['pitch']}, color={positioned['color']}")

    # ---------------------------------------------------------
    # ADD CHORD
    # ---------------------------------------------------------
    def add_chord(self, chord_dict):
        positioned = self.pixel_layout.layout_single(chord_dict)
        self.buffer.append(positioned)

        if self.canvas:
            self._draw_chord(positioned)
        else:
            print(f"[Renderer] Chord: {positioned['name']}")

    # ---------------------------------------------------------
    # ADD KEY CHANGE
    # ---------------------------------------------------------
    def add_key_change(self, key_item: dict):
        """
        Pridá zmenu tóniny do renderera.
        """
        key = key_item["key"]
        start = key_item["start"]

        if self.canvas:
            # zmažeme starý text tóniny
            self.canvas.delete("key_text")

            # vykreslíme novú tóninu vľavo hore
            self.canvas.create_text(
                300, 30,
                text=f"Key: {key}",
                fill="#FFFFAA",
                font=("Arial", 18, "bold"),
                tags="key_text"
            )
        else:
            print(f"[KEY] Zmena tóniny → {key} @ {start}")

        self.last_key = key

    # ---------------------------------------------------------
    # STAFF LINES
    # ---------------------------------------------------------
    def draw_staff(self, y_top=80, spacing=12, width=2000):
        if self.canvas is None:
            return

        for i in range(5):
            y = y_top + i * spacing
            self.canvas.create_line(0, y, width, y, fill="#666666", width=2)

    def draw_bass_staff(self, y_top=80 + 140, spacing=12, width=2000):
        self.draw_staff(y_top=y_top, spacing=spacing, width=width)

    # ---------------------------------------------------------
    # TRACK LABELS
    # ---------------------------------------------------------
    def draw_track_labels(self):
        if self.canvas is None:
            return

        self.canvas.create_text(
            40, 80 + 24,
            text="Melody",
            fill="#4DA6FF",
            font=("Arial", 12, "bold"),
            anchor="e"
        )

        self.canvas.create_text(
            40, 80 + 140 + 24,
            text="Bass",
            fill="#66CC66",
            font=("Arial", 12, "bold"),
            anchor="e"
        )

        self.canvas.create_text(
            40, 80 + 140 + 80,
            text="Drums",
            fill="#FF9933",
            font=("Arial", 12, "bold"),
            anchor="e"
        )

    # ---------------------------------------------------------
    # BARLINE
    # ---------------------------------------------------------
    def draw_barline(self, x, y_top=80, height=48 + 140):
        if self.canvas is None:
            return

        self.canvas.create_line(x, y_top, x, y_top + height, fill="#AAAAAA", width=2)

    # ---------------------------------------------------------
    # CHORD ABOVE BARLINE
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
    # MAIN CHORD DISPLAY
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
    # DRAW CHORD SYMBOL
    # ---------------------------------------------------------
    def _draw_chord(self, chord):
        if self.canvas is None:
            print(f"[Renderer] Chord: {chord['name']}")
            return

        x = chord["x"]
        y = chord["y"] - 40

        self.canvas.create_text(
            x, y,
            text=chord["name"],
            fill="#FFFFFF",
            font=self.chord_font
        )

    # ---------------------------------------------------------
    # RHYTHM SYMBOLS
    # ---------------------------------------------------------
    def draw_rhythm_symbol(self, x, y, duration):
        if self.canvas is None:
            return

        if duration >= 1.0:
            symbol = "𝅝"
        elif duration >= 0.5:
            symbol = "𝅗𝅥"
        elif duration >= 0.25:
            symbol = "♩"
        else:
            symbol = "♪"

        self.canvas.create_text(
            x - 10, y - 15,
            text=symbol,
            fill="#FFFFFF",
            font=("Arial", 14)
        )

    # ---------------------------------------------------------
    # DRAW NOTE
    # ---------------------------------------------------------
    def draw_note(self, note):
        if self.canvas is None:
            print(f"[Renderer] Note: pitch={note['pitch']}, color={note['color']}")
            return

        x = note["x"]
        y = note["y"]

        width = note["duration"] * 50
        height = 10

        track = note.get("track_type", "melody")
        color = self.track_colors.get(track, "#FFFFFF")

        if track == "drums":
            height = 6
            y += 20

        self.canvas.create_rectangle(
            x, y, x + width, y + height,
            fill=color,
            outline=""
        )

        self.draw_rhythm_symbol(x, y, note["duration"])

    # ---------------------------------------------------------
    # DRAW SLUR (LIGATÚRA)
    # ---------------------------------------------------------
    def draw_slur(self, start_note, end_note):
        if self.canvas is None:
            return

        x1 = start_note["x"]
        y1 = start_note["y"]
        x2 = end_note["x"]
        y2 = end_note["y"]

        # smerovanie oblúka – hore alebo dole
        direction = -20 if y2 < y1 else 20

        cx1 = x1 + (x2 - x1) * 0.3
        cy1 = y1 + direction

        cx2 = x1 + (x2 - x1) * 0.7
        cy2 = y2 + direction

        self.canvas.create_line(
            x1, y1,
            cx1, cy1,
            cx2, cy2,
            x2, y2,
            smooth=True,
            width=2,
            fill="#FFFFFF"
        )

    # ---------------------------------------------------------
    # RENDER FULL TIMELINE
    # ---------------------------------------------------------
    def render(self, timeline, current_chord=None):
        if self.canvas is None:
            print("[Renderer] Canvas nie je nastavený.")
            return

        self.draw_staff(y_top=80)
        self.draw_bass_staff(y_top=80 + 140)
        self.draw_track_labels()

        # taktové čiary + akordy nad nimi + tóniny
        for item in timeline:
            if item.get("type") == "barline":
                x = item.get("start", 0) * 40
                self.draw_barline(x)

                if "chord" in item:
                    self.draw_chord_above_bar(item["chord"], x)

            if item.get("type") == "key_change":
                self.add_key_change(item)

        # hlavný akord
        self.draw_chord(current_chord)

        # layout + vykreslenie nôt a akordov
        positioned = self.pixel_layout.layout_timeline(timeline)

        for item in positioned:
            item_type = item.get("type")
            if item_type == "chord":
                self._draw_chord(item)
            elif item_type == "barline":
                continue
            else:
                self.draw_note(item)

        # ligatúry (slurs) – pracujeme priamo s timeline
        for item in timeline:
            if item.get("type") == "slur":
                start = self.pixel_layout.layout_note(item["start_note"])
                end = self.pixel_layout.layout_note(item["end_note"])
                self.draw_slur(start, end)
