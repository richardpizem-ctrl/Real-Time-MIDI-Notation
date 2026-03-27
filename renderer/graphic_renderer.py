import pygame
import math
import time


class GraphicNotationRenderer:
    """
    Real-time grafický renderer pre MIDI notáciu.
    UIManager mu poskytuje surface, renderer NEVYTVÁRA okno.
    """

    def __init__(self, width=1200, height=500):
        self.width = width
        self.height = height

        # Renderer kreslí na vlastný surface
        self.screen = pygame.Surface((width, height))

        # Farby
        self.background_color = (20, 20, 20)
        self.staff_color = (200, 200, 200)

        # Farby podľa stopy
        self.track_colors = {
            "melody": (80, 160, 255),
            "bass": (120, 220, 120),
            "drums": (255, 150, 60),
            "chords": (255, 255, 120),
        }

        # Položky na vykreslenie
        # - items: globálne veci (barlines, key_changes, chords)
        # - items_by_track: noty rozdelené podľa stopy
        self.items = []
        self.items_by_track = {
            "melody": [],
            "bass": [],
            "drums": [],
            "chords": []
        }

        # 🔥 LIGATÚRY
        self.tie_items = []

        # Rozloženie
        self.staff_top = 80
        self.staff_spacing = 12
        self.bass_staff_top = 220
        self.drums_y = 300

        # Scrolling
        self.scroll_x = 0.0
        self.scroll_speed = 40.0  # px/s

        # Zoom
        self.zoom = 1.0

        # Konverzia času na pixely
        self.pixels_per_second = 120.0

        # Playhead
        self.playhead_time = 0.0

        # Dragovanie
        self.dragging = False
        self.last_mouse_x = 0

        # Čas
        self.clock = pygame.time.Clock()

        # Font cache
        pygame.font.init()
        self.font_chord = pygame.font.SysFont("Arial", 18)
        self.font_key = pygame.font.SysFont("Arial", 16)

    # ---------------------------------------------------------
    # API pre NotationProcessor
    # ---------------------------------------------------------
    def add_note(self, note):
        """
        Očakáva dict s kľúčmi:
        - type: "note"
        - start, duration, pitch, track_type, ...
        """
        if not isinstance(note, dict):
            print("Warning: add_note dostal neplatný objekt:", note)
            return

        track_type = note.get("track_type", "melody")

        if track_type not in self.items_by_track:
            # fallback – ak príde neznáma stopa, hodíme ju do melody
            track_type = "melody"

        # Ukladáme kópiu, aby sme si nepokazili originál
        self.items_by_track[track_type].append(note.copy())

    def add_barline(self, start_time):
        x = start_time * self.pixels_per_second
        self.items.append({"type": "barline", "x": x})

    def add_key_change(self, item):
        x = item["start"] * self.pixels_per_second
        self.items.append({"type": "key_change", "key": item["key"], "x": x})

    def add_chord(self, item):
        x = item["start"] * self.pixels_per_second
        self.items.append({"type": "chord", "name": item["name"], "x": x})

    # ---------------------------------------------------------
    # 🔥 LIGATÚRY – nový typ položky
    # ---------------------------------------------------------
    def add_tie(self, tie_item):
        start_x = tie_item["start"] * self.pixels_per_second
        end_x = tie_item["end"] * self.pixels_per_second

        self.tie_items.append({
            "type": "tie",
            "pitch": tie_item["pitch"],
            "start_x": start_x,
            "end_x": end_x,
            "track_type": tie_item.get("track_type", "melody")
        })

    def clear(self):
        self.items.clear()
        self.tie_items.clear()
        for k in self.items_by_track:
            self.items_by_track[k].clear()

    # ---------------------------------------------------------
    # Externé API pre UIManager
    # ---------------------------------------------------------
    def set_scroll_x(self, value):
        self.scroll_x = max(0.0, float(value))

    def set_zoom(self, value):
        self.zoom = max(0.2, min(3.0, float(value)))

    def set_playhead(self, timestamp):
        self.playhead_time = timestamp

    def tick(self, dt):
        self.update(dt)

    def update(self, dt):
        """Automatický posun timeline."""
        if not self.dragging:
            self.scroll_x += dt * self.scroll_speed

    # ---------------------------------------------------------
    # Kreslenie osnov
    # ---------------------------------------------------------
    def _draw_staff(self, y_top):
        spacing = self.staff_spacing * self.zoom
        y_top *= self.zoom

        for i in range(5):
            y = y_top + i * spacing
            pygame.draw.line(
                self.screen,
                self.staff_color,
                (40, y),
                (self.width - 40, y),
                int(2 * self.zoom)
            )

    def _draw_all_staffs(self):
        self._draw_staff(self.staff_top)
        self._draw_staff(self.bass_staff_top)

        # Drums – jedna čiara
        pygame.draw.line(
            self.screen,
            self.staff_color,
            (40, self.drums_y * self.zoom),
            (self.width - 40, self.drums_y * self.zoom),
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # 🔥 Kreslenie NOTOVEJ HLAVIČKY
    # ---------------------------------------------------------
    def _draw_note_head(self, item):
        x = (item["start"] * self.pixels_per_second - self.scroll_x) * self.zoom

        # Y podľa stopy
        track_type = item.get("track_type", "melody")

        if track_type == "melody":
            base_y = self.staff_top * self.zoom + 20
        elif track_type == "bass":
            base_y = self.bass_staff_top * self.zoom + 20
        elif track_type == "drums":
            base_y = self.drums_y * self.zoom - 5
        else:
            base_y = self.staff_top * self.zoom + 20

        # Rozmery hlavičky
        w = 14 * self.zoom
        h = 10 * self.zoom

        color = self.track_colors.get(track_type, (255, 255, 255))

        pygame.draw.ellipse(
            self.screen,
            color,
            (x, base_y, w, h)
        )

        return x, base_y, w, h

    # ---------------------------------------------------------
    # 🔥 STEMS (nožičky)
    # ---------------------------------------------------------
    def _draw_stem(self, item):
        x, y, w, h = self._draw_note_head(item)

        # Nožička ide hore (klasický zápis)
        stem_x = x + w
        stem_y_top = y - 30 * self.zoom
        stem_y_bottom = y + h / 2

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (stem_x, stem_y_bottom),
            (stem_x, stem_y_top),
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # 🔥 Kreslenie ligatúry (oblúk)
    # ---------------------------------------------------------
    def _draw_tie(self, tie):
        x1 = (tie["start_x"] - self.scroll_x) * self.zoom
        x2 = (tie["end_x"] - self.scroll_x) * self.zoom

        if x2 < 0 or x1 > self.width:
            return

        width = x2 - x1
        arc_height = 18 * self.zoom

        # Zatiaľ fixne nad hornou osnovou – neskôr môžeme posúvať podľa pitch/track
        rect = pygame.Rect(
            x1,
            self.staff_top * self.zoom + 40,
            width,
            arc_height
        )

        pygame.draw.arc(
            self.screen,
            (230, 230, 230),
            rect,
            math.pi,
            2 * math.pi,
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # Hlavné kreslenie
    # ---------------------------------------------------------
    def render(self):
        self.screen.fill(self.background_color)

        # Osnovy
        self._draw_all_staffs()

        # -----------------------------------------------------
        # 1) Globálne položky – barlines, chords, key_changes
        # -----------------------------------------------------
        for item in self.items:
            if item["type"] == "barline":
                x = (item["x"] - self.scroll_x) * self.zoom

                color = (230, 230, 230)
                thickness = int(2 * self.zoom)

                # Horná osnova
                pygame.draw.line(
                    self.screen,
                    color,
                    (x, self.staff_top * self.zoom),
                    (x, (self.staff_top + 4 * self.staff_spacing) * self.zoom),
                    thickness
                )

                # Basová osnova
                pygame.draw.line(
                    self.screen,
                    color,
                    (x, self.bass_staff_top * self.zoom),
                    (x, (self.bass_staff_top + 4 * self.staff_spacing) * self.zoom),
                    thickness
                )

                # Drums
                pygame.draw.line(
                    self.screen,
                    color,
                    (x, self.drums_y * self.zoom - 10),
                    (x, self.drums_y * self.zoom + 10),
                    thickness
                )

            elif item["type"] == "chord":
                x = (item["x"] - self.scroll_x) * self.zoom
                text = self.font_chord.render(item["name"], True, (255, 255, 120))
                self.screen.blit(text, (x + 5, 40))

            elif item["type"] == "key_change":
                x = (item["x"] - self.scroll_x) * self.zoom
                text = self.font_key.render(item["key"], True, (255, 200, 200))
                self.screen.blit(text, (x + 5, 20))

        # -----------------------------------------------------
        # 2) Noty – multi-track, v definovanom poradí vrstiev
        # -----------------------------------------------------
        track_draw_order = ["melody", "chords", "bass", "drums"]

        for track_type in track_draw_order:
            for note in self.items_by_track.get(track_type, []):
                if note.get("type") != "note":
                    continue
                # Zabezpečíme, že track_type je v note
                note["track_type"] = track_type
                self._draw_stem(note)

        # ---------------------------------------------------------
        # 🔥 LIGATÚRY
        # ---------------------------------------------------------
        for tie in self.tie_items:
            self._draw_tie(tie)

        # ---------------------------------------------------------
        # PLAYHEAD LINE
        # ---------------------------------------------------------
        playhead_x = (self.playhead_time * self.pixels_per_second - self.scroll_x) * self.zoom

        if 0 <= playhead_x <= self.width:
            pygame.draw.line(
                self.screen,
                (230, 230, 230),
                (playhead_x, 0),
                (playhead_x, self.height),
                int(3 * self.zoom)
            )

        return self.screen
