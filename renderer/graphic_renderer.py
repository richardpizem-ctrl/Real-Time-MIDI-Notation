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

        # Harmonické farby podľa role
        self.harmony_colors = {
            "root": (255, 255, 255),
            "chord_tone": (120, 220, 255),
            "tension": (255, 140, 200),
            "scale_tone": (180, 220, 180),
            "outside": (255, 90, 90),
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
        self.font_articulation = pygame.font.SysFont("Arial", 22, bold=True)

        # Track visibility – základ pre Track Manager
        self.track_visible = {
            "melody": True,
            "bass": True,
            "drums": True,
            "chords": True,
        }

        # Caching osnov – kreslia sa len pri zmene zoomu
        self.staff_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.needs_staff_redraw = True

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

        n = note.copy()
        n["track_type"] = track_type

        # Harmonická farba, ak je k dispozícii
        harmony_role = n.get("harmony_role")
        if harmony_role in self.harmony_colors:
            n["_color"] = self.harmony_colors[harmony_role]
        else:
            base_color = self.track_colors.get(track_type, (255, 255, 255))
            velocity = n.get("velocity", 100)
            n["_color"] = self._velocity_color(base_color, velocity)

        self.items_by_track[track_type].append(n)

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

    def set_zoom(self, value):
        self.zoom = max(0.2, min(3.0, float(value)))
        self.needs_staff_redraw = True

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
    # Pitch → Y konverzia
    # ---------------------------------------------------------
    def _pitch_to_y(self, pitch, track_type):
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

        color = item.get("_color")
        if color is None:
            base_color = self.track_colors.get(item["track_type"], (255, 255, 255))
            color = self._velocity_color(base_color, item.get("velocity", 100))

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
    # ARTIKULÁCIE (staccato, accent, tenuto, marcato)
    # ---------------------------------------------------------
    def _draw_articulations(self, item, x, y, w, h):
        articulation = item.get("articulation")
        if not articulation:
            return

        articulation = articulation.lower()

        symbols = {
            "staccato": "·",
            "accent": ">",
            "tenuto": "–",
            "marcato": "^"
        }

        if articulation not in symbols:
            return

        symbol = symbols[articulation]
        text = self.font_articulation.render(symbol, True, (255, 255, 255))

        if item["pitch"] >= 64:
            pos_y = y - 18 * self.zoom
        else:
            pos_y = y + h + 12 * self.zoom

        pos_x = x + w / 2
        rect = text.get_rect(center=(pos_x, pos_y))
        self.screen.blit(text, rect)

    # ---------------------------------------------------------
    # Kreslenie hlavičky
    # ---------------------------------------------------------
    def _draw_note_head(self, item):
        x = (item["start"] * self.pixels_per_second - self.scroll_x) * self.zoom
        y = self._pitch_to_y(item["pitch"], item["track_type"])

        w = 14 * self.zoom
        h = 10 * self.zoom

        color = item.get("_color")
        if color is None:
            base_color = self.track_colors.get(item["track_type"], (255, 255, 255))
            color = self._velocity_color(base_color, item.get("velocity", 100))

        pygame.draw.ellipse(self.screen, color, (x, y, w, h))

        x_center = x + w / 2
        self._draw_ledger_lines(x_center, item["pitch"], item["track_type"])
        self._draw_dynamic_marking(item, x, y, h)
        self._draw_articulations(item, x, y, w, h)

        return x, y, w, h

    # ---------------------------------------------------------
    # STEM
    # ---------------------------------------------------------
    def _draw_stem(self, item):
        x, y, w, h = self._draw_note_head(item)

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
    # Ligatúry – SMART TIES
    # ---------------------------------------------------------
    def _draw_tie(self, tie):
        x1 = (tie["start_x"] - self.scroll_x) * self.zoom
        x2 = (tie["end_x"] - self.scroll_x) * self.zoom

        if x2 <= x1:
            return
        if x2 < 0 or x1 > self.width:
            return

        width = x2 - x1
        pitch = tie["pitch"]
        track_type = tie.get("track_type", "melody")
        y_note = self._pitch_to_y(pitch, track_type)

        base_height = 8 * self.zoom
        extra_height = min(24 * self.zoom, max(0, width * 0.08))
        arc_height = base_height + extra_height * 0.4

        offset = 6 * self.zoom

        if pitch >= 64:
            center_y = y_note - offset
            rect = pygame.Rect(x1, center_y - arc_height, width, arc_height * 2)
            start_angle = 0
            end_angle = math.pi
        else:
            center_y = y_note + offset
            rect = pygame.Rect(x1, center_y - arc_height, width, arc_height * 2)
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

    def _draw_all_staffs_to_surface(self, surf):
        spacing = self.staff_spacing * self.zoom

        for i in range(5):
            y = self.staff_top * self.zoom + i * spacing
            pygame.draw.line(
                surf,
                self.staff_color,
                (40, y),
                (self.width - 40, y),
                int(2 * self.zoom)
            )

        for i in range(5):
            y = self.bass_staff_top * self.zoom + i * spacing
            pygame.draw.line(
                surf,
                self.staff_color,
                (40, y),
                (self.width - 40, y),
                int(2 * self.zoom)
            )

        pygame.draw.line(
            surf,
            self.staff_color,
            (40, self.drums_y * self.zoom),
            (self.width - 40, self.drums_y * self.zoom),
            int(2 * self.zoom)
        )

    # ---------------------------------------------------------
    # Playhead – DAW + glow + pulz
    # ---------------------------------------------------------
    def _draw_playhead(self):
        x = (self.playhead_time * self.pixels_per_second - self.scroll_x) * self.zoom

        top_y = 30
        bottom_y = self.height - 30

        t = time.time()
        pulse = 0.5 + 0.5 * math.sin(t * 2.5)

        glow_width = 18 * self.zoom
        glow_alpha = int(40 + 80 * pulse)
        glow_surface = pygame.Surface((int(glow_width), int(bottom_y - top_y)), pygame.SRCALPHA)
        pygame.draw.rect(
            glow_surface,
            (255, 80, 80, glow_alpha),
            (0, 0, glow_width, bottom_y - top_y)
        )
        self.screen.blit(glow_surface, (x - glow_width / 2, top_y))

        thickness_main = max(2, int(2 * self.zoom))
        pygame.draw.line(
            self.screen,
            (255, 80, 80),
            (x, top_y),
            (x, bottom_y),
            thickness_main
        )

        thickness_inner = 1
        pygame.draw.line(
            self.screen,
            (255, 255, 255),
            (x, top_y),
            (x, bottom_y),
            thickness_inner
        )

    # ---------------------------------------------------------
    # Render
    # ---------------------------------------------------------
    def render(self):
        self.screen.fill(self.background_color)

        if self.needs_staff_redraw:
            self.staff_surface.fill((0, 0, 0, 0))
            self._draw_all_staffs_to_surface(self.staff_surface)
            self.needs_staff_redraw = False

        self.screen.blit(self.staff_surface, (0, 0))

        for item in self.items:
            if item["type"] == "barline":
                x = (item["x"] - self.scroll_x) * self.zoom
                color = (230, 230, 230)
                thickness = int(2 * self.zoom)

                pygame.draw.line(
                    self.screen, color,
                    (x, self.staff_top * self.zoom),
                    (x, (self.staff_top + 4 * self.staff_spacing) * self.zoom),
                    thickness
                )

                pygame.draw.line(
                    self.screen, color,
                    (x, self.bass_staff_top * self.zoom),
                    (x, (self.bass_staff_top + 4 * self.staff_spacing) * self.zoom),
                    thickness
                )

                pygame.draw.line(
                    self.screen, color,
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
                text = self.font_key.render(item["key"], True, (200, 200, 255))
                self.screen.blit(text, (x + 5, 60))

        for track_type, notes in self.items_by_track.items():
            if not self.track_visible.get(track_type, True):
                continue
            for note in notes:
                self._draw_duration_bar(note)

        for track_type, notes in self.items_by_track.items():
            if not self.track_visible.get(track_type, True):
                continue
            for note in notes:
                self._draw_stem(note)

        for tie in self.tie_items:
            track_type = tie.get("track_type", "melody")
            if not self.track_visible.get(track_type, True):
                continue
            self._draw_tie(tie)

        self._draw_playhead()

        return self.screen
