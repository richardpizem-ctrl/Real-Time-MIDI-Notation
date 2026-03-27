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

        self.screen = pygame.Surface((width, height))

        self.background_color = (20, 20, 20)
        self.staff_color = (200, 200, 200)

        # Základné farby stôp
        self.track_colors = {
            "melody": (80, 160, 255),
            "bass": (120, 220, 120),
            "drums": (255, 150, 60),
            "chords": (255, 255, 120),
        }

        self.items = []
        self.items_by_track = {
            "melody": [],
            "bass": [],
            "drums": [],
            "chords": []
        }

        self.tie_items = []

        self.staff_top = 80
        self.staff_spacing = 12
        self.bass_staff_top = 220
        self.drums_y = 300

        self.scroll_x = 0.0
        self.scroll_speed = 40.0

        self.zoom = 1.0

        self.pixels_per_second = 120.0

        self.playhead_time = 0.0

        self.dragging = False
        self.last_mouse_x = 0

        self.clock = pygame.time.Clock()

        pygame.font.init()
        self.font_chord = pygame.font.SysFont("Arial", 18)
        self.font_key = pygame.font.SysFont("Arial", 16)
        self.font_dynamic = pygame.font.SysFont("Arial", 14)

        # Track visibility – základ pre Track Manager
        self.track_visible = {
            "melody": True,
            "bass": True,
            "drums": True,
            "chords": True,
        }

    # ---------------------------------------------------------
    # API pre NotationProcessor
    # ---------------------------------------------------------
    def add_note(self, note):
        if not isinstance(note, dict):
            print("Warning: add_note dostal neplatný objekt:", note)
            return

        track_type = note.get("track_type", "melody")

        if track_type not in self.items_by_track:
            track_type = "melody"

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
    # Externé API
    # ---------------------------------------------------------
    def set_scroll_x(self, value):
        self.scroll_x = max(0.0, float(value))

        # ---------------------------------------------------------
    def set_zoom(self, value):
        self.zoom = max(0.2, min(3.0, float(value)))

    def set_playhead(self, timestamp):
        self.playhead_time = timestamp

    def set_track_visible(self, track_type, visible: bool):
        if track_type in self.track_visible:
            self.track_visible[track_type] = bool(visible)

    def tick(self, dt):
        self.update(dt)

    def update(self, dt):
        if not self.dragging:
            self.scroll_x += dt * self.scroll_speed

    # ---------------------------------------------------------
    # Pitch → Y konverzia (lepšie podľa kľúča)
    # ---------------------------------------------------------
    def _pitch_to_y(self, pitch, track_type):
        """
        MIDI pitch → Y pozícia na osnove.
        Melody: treble clef, referenčný tón G4 (67)
        Bass: bass clef, referenčný tón E3 (52)
        """
        if track_type == "melody":
            base_pitch = 67  # G4
            base_y = self.staff_top * self.zoom + 2 * self.staff_spacing * self.zoom
        elif track_type == "bass":
            base_pitch = 52  # E3
            base_y = self.bass_staff_top * self.zoom + 2 * self.staff_spacing * self.zoom
        else:
            return self.drums_y * self.zoom

        offset = (base_pitch - pitch) * (self.staff_spacing / 2) * self.zoom
        return base_y + offset

    # ---------------------------------------------------------
    # Velocity → farba
    # ---------------------------------------------------------
    def _velocity_color(self, base_color, velocity):
        factor = 0.4 + (velocity / 127) * 0.6
        r = min(255, int(base_color[0] * factor))
        g = min(255, int(base_color[1] * factor))
        b = min(255, int(base_color[2] * factor))
        return (r, g, b)

    # ---------------------------------------------------------
    # Duration bar
    # ---------------------------------------------------------
    def _draw_duration_bar(self, item):
        start_x = (item["start"] * self.pixels_per_second - self.scroll_x) * self.zoom
        end_x = ((item["start"] + item["duration"]) * self.pixels_per_second - self.scroll_x) * self.zoom
        width = max(0, end_x - start_x)

        y = self._pitch_to_y(item["pitch"], item["track_type"])

        color = self._velocity_color(
            self.track_colors.get(item["track_type"], (255, 255, 255)),
            item.get("velocity", 100)
        )

        pygame.draw.rect(
            self.screen,
            color,
            (start_x + 10 * self.zoom, y + 4 * self.zoom, width, 3 * self.zoom)
        )

    # ---------------------------------------------------------
    # Ledger lines
    # ---------------------------------------------------------
    def _draw_ledger_lines(self, x_center, pitch, track_type):
        if track_type == "melody":
            staff_top = self.staff_top * self.zoom
        elif track_type == "bass":
            staff_top = self.bass_staff_top * self.zoom
        else:
            return

        spacing = self.staff_spacing * self.zoom
        top_line_y = staff_top
        bottom_line_y = staff_top + 4 * spacing

        y = self._pitch_to_y(pitch, track_type)
        line_length = 18 * self.zoom
        half_len = line_length / 2
        color = (180, 180, 180)

        # nad osnovou
        if y < top_line_y:
            step = spacing / 2
            current_y = top_line_y - step
            while current_y + 1 > y:
                pygame.draw.line(
                    self.screen,
                    color,
                    (x_center - half_len, current_y),
                    (x_center + half_len, current_y),
                    int(2 * self.zoom)
                )
                current_y -= step

        # pod osnovou
        if y > bottom_line_y:
            step = spacing / 2
            current_y = bottom_line_y + step
            while current_y - 1 < y:
                pygame.draw.line(
                    self.screen,
                    color,
                    (x_center - half_len, current_y),
                    (x_center + half_len, current_y),
                    int(2 * self.zoom)
                )
                current_y += step

    # ---------------------------------------------------------
    # Dynamika
    # ---------------------------------------------------------
    def _draw_dynamic_marking(self, item, x, y, h):
        dyn = item.get("dynamic")
        if not dyn:
            return

        dyn = str(dyn).lower()
        if dyn not in ("pp", "p", "mp", "mf", "f", "ff"):
            return

        intensity = {
            "pp": 0.3,
            "p": 0.45,
            "mp": 0.6,
            "mf": 0.75,
            "f": 0.9,
            "ff": 1.0
        }[dyn]

        base_color = (230, 230, 230)
        color = (
            int(base_color[0] * intensity),
            int(base_color[1] * intensity),
            int(base_color[2] * intensity),
        )

        text = self.font_dynamic.render(dyn, True, color)
        text_rect = text.get_rect()
        text_rect.midtop = (x + (14 * self.zoom) / 2, y + h + 6 * self.zoom)
        self.screen.blit(text, text_rect)

    # ---------------------------------------------------------
    # Kreslenie hlavičky
    # ---------------------------------------------------------
    def _draw_note_head(self, item):
        x = (item["start"] * self.pixels_per_second - self.scroll_x) * self.zoom
        y = self._pitch_to_y(item["pitch"], item["track_type"])

        w = 14 * self.zoom
        h = 10 * self.zoom

        color = self._velocity_color(
            self.track_colors.get(item["track_type"], (255, 255, 255)),
            item.get("velocity", 100)
        )

        pygame.draw.ellipse(
            self.screen,
            color,
            (x, y, w, h)
        )

        # ledger lines + dynamika
        x_center = x + w / 2
        self._draw_ledger_lines(x_center, item["pitch"], item["track_type"])
        self._draw_dynamic_marking(item, x, y, h)

        return x, y, w, h

    # ---------------------------------------------------------
    # STEM
    # ---------------------------------------------------------
    def _draw_stem(self, item):
        x, y, w, h = self._draw_note_head(item)

        # jednoduché pravidlo: vyššie tóny stem dole, nižšie hore
        if item["pitch"] >= 64:
            stem_x = x
            stem_y_top = y + h
            stem_y_bottom = y + h + 30 * self.zoom
        else:
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

        return stem_x, stem_y_top, stem_y_bottom

    # ---------------------------------------------------------
    # Beamovanie osminových nôt
    # ---------------------------------------------------------
    def _group_beams(self, notes, beat_duration=0.5):
        """
        Jednoduché beamovanie:
        - berieme noty s duration <= beat_duration (napr. osminy)
        - spájame susedné, ak sú časovo blízko
        """
        groups = []
        current = []

        notes_sorted = sorted(notes, key=lambda n: n["start"])

        for n in notes_sorted:
            if n.get("duration", 0) > beat_duration:
                if len(current) >= 2:
                    groups.append(current)
                current = []
                continue

            if not current:
                current = [n]
            else:
                prev = current[-1]
                gap = n["start"] - (prev["start"] + prev.get("duration", 0))
                if gap <= beat_duration * 0.3:
                    current.append(n)
                else:
                    if len(current) >= 2:
                        groups.append(current)
                    current = [n]

        if len(current) >= 2:
            groups.append(current)

        return groups

    def _draw_beam_group(self, group, track_type):
        """
        Jednoduchý beam: jedna hrubá čiara medzi stems.
        """
        stem_points = []
        for note in group:
            note["track_type"] = track_type
            x, y, w, h = self._draw_note_head(note)
            if note["pitch"] >= 64:
                stem_x = x
                stem_y = y + h + 30 * self.zoom
            else:
                stem_x = x + w
                stem_y = y - 30 * self.zoom
            stem_points.append((stem_x, stem_y))

        if len(stem_points) < 2:
            return

        stem_points.sort(key=lambda p: p[0])
        y_avg = sum(p[1] for p in stem_points) / len(stem_points)

        x_start = stem_points[0][0]
        x_end = stem_points[-1][0]

        thickness = int(4 * self.zoom)

        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (x_start, y_avg),
            (x_end, y_avg),
            thickness
        )

    # ---------------------------------------------------------
    # Ligatúry – tvar podľa pitch
    # ---------------------------------------------------------
    def _draw_tie(self, tie):
        x1 = (tie["start_x"] - self.scroll_x) * self.zoom
        x2 = (tie["end_x"] - self.scroll_x) * self.zoom

        if x2 < 0 or x1 > self.width:
            return

        width = x2 - x1
        pitch = tie["pitch"]
        track_type = tie.get("track_type", "melody")
        y = self._pitch_to_y(pitch, track_type)

        arc_height = 12 * self.zoom

        rect = pygame.Rect(
            x1,
            y - arc_height,
            width,
            arc_height * 2
        )

        # ak je tón vyššie, oblúk ide „nadol“, ak nižšie, „nahor“
        if pitch >= 64:
            start_angle = 0
            end_angle = math.pi
        else:
            start_angle = math.pi
            end_angle = 2 * math.pi

        pygame.draw.arc(
            self.screen,
            (230, 230, 230),
            rect,
            start_angle,
            end_angle,
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # Osnovy
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

        pygame.draw.line(
            self.screen,
            self.staff_color,
            (40, self.drums_y * self.zoom),
            (self.width - 40, self.drums_y * self.zoom),
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # Render
    # ---------------------------------------------------------
    def render(self):
        self.screen.fill(self.background_color)

        self._draw_all_staffs()

        # Globálne položky
        for item in self.items:
            if item["type"] == "barline":
                x = (item["x"] - self.scroll_x) * self.zoom
                color = (230, 230, 230)
                thickness = int(2 * self.zoom)

                pygame.draw.line(self.screen, color,
                                 (x, self.staff_top * self.zoom),
                                 (x, (self.staff_top + 4 * self.staff_spacing) * self.zoom),
                                 thickness)

                pygame.draw.line(self.screen, color,
                                 (x, self.bass_staff_top * self.zoom),
                                 (x, (self.bass_staff_top + 4 * self.staff_spacing) * self.zoom),
                                 thickness)

                pygame.draw.line(self.screen, color,
                                 (x, self.drums_y * self.zoom - 10),
                                 (x, self.drums_y * self.zoom + 10),
                                 thickness)

            elif item["type"] == "chord":
                x = (item["x"] - self.scroll_x) * self.zoom
                text = self.font_chord.render(item["name"], True, (255, 255, 120))
                self.screen.blit(text, (x + 5, 40))

            elif item["type"] == "key_change":
                x = (item["x"] - self.scroll_x) * self.zoom
                text = self.font_key.render(item["key"], True, (255, 200, 200))
                self.screen.blit(text, (x + 5, 20))

        # Noty podľa vrstiev
        track_draw_order = ["melody", "chords", "bass", "drums"]

        for track_type in track_draw_order:
            if not self.track_visible.get(track_type, True):
                continue

            notes = self.items_by_track.get(track_type, [])

            # Beamovanie – len melody a bass
            if track_type in ("melody", "bass"):
                beam_groups = self._group_beams(notes)
                for group in beam_groups:
                    self._draw_beam_group(group, track_type)

            for note in notes:
                if note.get("type") != "note":
                    continue

                note["track_type"] = track_type

                self._draw_duration_bar(note)
                self._draw_stem(note)

        # Ligatúry
        for tie in self.tie_items:
            self._draw_tie(tie)

        # Playhead
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
