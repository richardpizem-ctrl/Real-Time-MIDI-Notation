import pygame
import time
from typing import List, Dict, Any, Tuple, Optional


class GraphicNotationRenderer:
    def __init__(self, width, height, track_manager):
        self.width = width
        self.height = height
        self.track_manager = track_manager

        try:
            self.surface = pygame.Surface((width, height))
        except Exception:
            self.surface = None

        try:
            self.font = pygame.font.SysFont("Arial", 18)
        except Exception:
            self.font = None

        # Staff cache
        self.staff_cache = None
        self.staff_cache_width = width
        self.staff_cache_height = 140

        # Layout
        self.margin_left = 40
        self.margin_top = 20
        self.staff_line_spacing = 12

        # Real‑time engine
        self.playback_time = 0.0
        self.last_frame_time = time.time()

        # AUTO‑SCROLL ENGINE
        self.zoom = 1.0
        self.scroll_speed = 120.0
        self.scroll_offset = 0.0

        # Tempo
        self.bpm = 120.0
        self.beats_per_bar = 4

        # Playhead (center of screen)
        self.playhead_x = width // 2

    # ---------------------------------------------------------
    # CONFIG
    # ---------------------------------------------------------
    def set_playback_time(self, t: float):
        self.playback_time = float(t)

    def set_bpm(self, bpm: float):
        try:
            bpm = float(bpm)
            if bpm > 0:
                self.bpm = bpm
        except Exception:
            pass

    def set_zoom(self, zoom: float):
        try:
            zoom = float(zoom)
            if zoom > 0.1:
                self.zoom = zoom
        except Exception:
            pass

    # ---------------------------------------------------------
    # STAFF LINES (CACHED)
    # ---------------------------------------------------------
    def _render_staff_lines(self):
        if self.staff_cache is not None:
            return self.staff_cache

        surf = pygame.Surface(
            (self.staff_cache_width, self.staff_cache_height),
            pygame.SRCALPHA
        )
        surf.fill((0, 0, 0, 0))

        y_start = self.margin_top
        for i in range(5):
            y = y_start + i * self.staff_line_spacing
            pygame.draw.line(
                surf,
                (200, 200, 200),
                (self.margin_left, y),
                (self.width - 20, y),
                2
            )

        self.staff_cache = surf
        return surf

    # ---------------------------------------------------------
    # REAL‑TIME ENGINE + AUTO‑SCROLL
    # ---------------------------------------------------------
    def _update_time(self):
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        self.playback_time += dt
        self.scroll_offset += dt * self.scroll_speed * self.zoom

        return dt

    # ---------------------------------------------------------
    # POSITIONING
    # ---------------------------------------------------------
    def _pitch_to_y(self, midi: int) -> float:
        return self.margin_top + (60 - midi) * 1.1

    def _time_to_x(self, timestamp: float) -> float:
        # AUTO‑SCROLL: svet sa posúva, playhead stojí
        return (
            self.playhead_x
            + (timestamp - self.playback_time) * self.scroll_speed * self.zoom
        )

    # ---------------------------------------------------------
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _get_track_color(self, track_id: int, active_track_id: Optional[int]) -> Tuple[int, int, int]:
        try:
            base_color = self.track_manager.get_color(track_id)
        except Exception:
            base_color = (255, 255, 255)

        if active_track_id is None or track_id != active_track_id:
            return base_color

        r, g, b = base_color
        r = min(255, int(r * 1.25) + 15)
        g = min(255, int(g * 1.25) + 15)
        b = min(255, int(b * 1.25) + 15)
        return (r, g, b)

    # ---------------------------------------------------------
    # DRAW NOTE HEAD
    # ---------------------------------------------------------
    def _draw_note(self, surface, x: float, y: float, color: Tuple[int, int, int]):
        rect = pygame.Rect(int(x), int(y), 16, 12)
        pygame.draw.ellipse(surface, color, rect)
        pygame.draw.ellipse(surface, (0, 0, 0), rect, 2)

    # ---------------------------------------------------------
    # GROUP NOTES INTO CHORDS
    # ---------------------------------------------------------
    def _group_notes(self, notes: List[Dict[str, Any]]):
        groups = {}
        for note in notes:
            if not isinstance(note, dict):
                continue

            midi = note.get("pitch") or note.get("note")
            track_id = note.get("track_id")
            timestamp = note.get("timestamp", 0.0)

            if midi is None or track_id is None:
                continue

            key = (float(timestamp), int(track_id))
            groups.setdefault(key, []).append(note)

        return groups

    # ---------------------------------------------------------
    # BARLINES
    # ---------------------------------------------------------
    def _draw_barlines(self):
        if self.bpm <= 0:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar_index = int(self.playback_time // seconds_per_bar)
        bars_to_draw = range(current_bar_index - 4, current_bar_index + 12)

        for bar_index in bars_to_draw:
            if bar_index < 0:
                continue

            bar_time = bar_index * seconds_per_bar
            x = self._time_to_x(bar_time)

            if x < 0 or x > self.width:
                continue

            pygame.draw.line(
                self.surface,
                (255, 255, 180) if bar_index % 1 == 0 else (90, 90, 90),
                (int(x), 0),
                (int(x), self.height),
                3 if bar_index % 1 == 0 else 1
            )

    # ---------------------------------------------------------
    # TIMELINE RULER (NEW)
    # ---------------------------------------------------------
    def _draw_timeline_ruler(self):
        if self.bpm <= 0 or self.font is None:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar_index = int(self.playback_time // seconds_per_bar)
        bars_to_draw = range(current_bar_index - 4, current_bar_index + 12)

        for bar_index in bars_to_draw:
            if bar_index < 0:
                continue

            bar_time = bar_index * seconds_per_bar
            x = self._time_to_x(bar_time)

            if 0 <= x <= self.width:
                label = self.font.render(str(bar_index + 1), True, (230, 230, 230))
                self.surface.blit(label, (int(x) + 4, 0))

    # ---------------------------------------------------------
    # PLAYHEAD
    # ---------------------------------------------------------
    def _draw_playhead(self):
        pygame.draw.line(
            self.surface,
            (255, 80, 80),
            (self.playhead_x, 0),
            (self.playhead_x, self.height),
            3
        )

    # ---------------------------------------------------------
    # MAIN DRAW
    # ---------------------------------------------------------
    def draw(self, notes):
        if self.surface is None:
            self.surface = pygame.Surface((self.width, self.height))

        self._update_time()
        self.surface.fill((25, 25, 25))

        # TIMELINE RULER (NEW)
        self._draw_timeline_ruler()

        staff = self._render_staff_lines()
        self.surface.blit(staff, (0, 0))

        self._draw_barlines()

        if not isinstance(notes, (list, tuple)):
            self._draw_playhead()
            return self.surface

        try:
            active_track_id = self.track_manager.get_active_track()
        except Exception:
            active_track_id = None

        grouped = self._group_notes(list(notes))

        for (timestamp, track_id), chord_notes in grouped.items():
            try:
                if not self.track_manager.is_visible(track_id):
                    continue
            except Exception:
                pass

            color = self._get_track_color(track_id, active_track_id)
            base_x = self._time_to_x(timestamp)

            for idx, note in enumerate(chord_notes):
                midi = note.get("pitch") or note.get("note")
                if midi is None:
                    continue

                y = self._pitch_to_y(int(midi))
                x = base_x + idx * 6
                self._draw_note(self.surface, x, y, color)

        self._draw_playhead()
        return self.surface
