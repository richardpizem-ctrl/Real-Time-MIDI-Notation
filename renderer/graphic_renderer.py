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

        # Time / playback
        self.playback_time = 0.0
        self.last_frame_time = time.time()

        # View
        self.zoom = 1.0
        self.scroll_speed = 120.0
        self.scroll_offset = 0.0

        # Tempo / meter
        self.bpm = 120.0
        self.beats_per_bar = 4

        # Playhead
        self.playhead_x = width // 2

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
    # TIME / SCROLL
    # ---------------------------------------------------------
    def _update_time(self):
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        self.playback_time += dt
        self.scroll_offset += dt * self.scroll_speed * self.zoom

        return dt

    # ---------------------------------------------------------
    # COORDINATE MAPPING
    # ---------------------------------------------------------
    def _pitch_to_y(self, midi: int) -> float:
        return self.margin_top + (60 - midi) * 1.1

    def _time_to_x(self, timestamp: float) -> float:
        return (
            self.playhead_x
            + (timestamp - self.playback_time) * self.scroll_speed * self.zoom
        )

    # ---------------------------------------------------------
    # TRACK COLOR / ACTIVE TRACK BOOST (B/)
    # ---------------------------------------------------------
    def _get_track_color(self, track_id: int, active_track_id: Optional[int]) -> Tuple[int, int, int]:
        """
        Vracia farbu stopy s podporou zvýraznenia aktívnej stopy.
        """
        try:
            base_color = self.track_manager.get_color(track_id)
        except Exception:
            base_color = (255, 255, 255)

        # Ak nie je aktívna stopa alebo táto stopa nie je aktívna → normálna farba
        if active_track_id is None or track_id != active_track_id:
            # Jemné stlmenie neaktívnych stôp
            r, g, b = base_color
            return (int(r * 0.55), int(g * 0.55), int(b * 0.55))

        # Zvýraznenie aktívnej stopy
        r, g, b = base_color
        r = min(255, int(r * 1.25) + 15)
        g = min(255, int(g * 1.25) + 15)
        b = min(255, int(b * 1.25) + 15)
        return (r, g, b)

    # ---------------------------------------------------------
    # NOTE DRAWING
    # ---------------------------------------------------------
    def _draw_note(self, surface, x: float, y: float, color: Tuple[int, int, int]):
        rect = pygame.Rect(int(x), int(y), 16, 12)
        pygame.draw.ellipse(surface, color, rect)
        pygame.draw.ellipse(surface, (0, 0, 0), rect, 2)

    # ---------------------------------------------------------
    # LIGATURE / SIMPLE BEAM DRAWING (LEGACY)
    # ---------------------------------------------------------
    def _draw_ligature(self, x1: float, x2: float, y: float, color: Tuple[int, int, int]):
        x1i = int(x1)
        x2i = int(x2)
        yi = int(y)
        pygame.draw.line(self.surface, color, (x1i, yi), (x2i, yi), 4)

    # ---------------------------------------------------------
    # GROUPING BEAM DRAWING (SLOPED, MULTI-LEVEL)
    # ---------------------------------------------------------
    def _draw_beam(self, x1: float, y1: float, x2: float, y2: float, color: Tuple[int, int, int], levels: int = 1):
        x1i = int(x1)
        x2i = int(x2)
        y1f = float(y1)
        y2f = float(y2)

        for level in range(levels):
            offset = level * 4
            y1i = int(y1f - offset)
            y2i = int(y2f - offset)
            pygame.draw.line(self.surface, color, (x1i, y1i), (x2i, y2i), 3)

    # ---------------------------------------------------------
    # CHORD GROUPING (MULTI-HEAD CHORDS)
    # ---------------------------------------------------------
    def _group_notes(self, notes: List[Dict[str, Any]]):
        groups: Dict[Tuple[float, int], List[Dict[str, Any]]] = {}
        time_quantum = 0.02

        for note in notes:
            if not isinstance(note, dict):
                continue

            midi = note.get("pitch") or note.get("note")
            track_id = note.get("track_id")
            timestamp = note.get("timestamp", 0.0)

            if midi is None or track_id is None:
                continue

            try:
                t = float(timestamp)
            except Exception:
                t = 0.0

            quantized_time = round(t / time_quantum) * time_quantum
            key = (quantized_time, int(track_id))
            groups.setdefault(key, []).append(note)

        return groups

    # ---------------------------------------------------------
    # BARLINES / GRID / RULER / MEASURE NUMBERS
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
                (255, 255, 180),
                (int(x), 0),
                (int(x), self.height),
                3
            )

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

    def _draw_grid_lines(self):
        if self.bpm <= 0:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar_index = int(self.playback_time // seconds_per_bar)
        bars_to_draw = range(current_bar_index - 4, current_bar_index + 12)

        for bar_index in bars_to_draw:
            if bar_index < 0:
                continue

            bar_start = bar_index * seconds_per_bar

            for beat in range(self.beats_per_bar):
                t = bar_start + beat * seconds_per_beat
                x = self._time_to_x(t)
                if 0 <= x <= self.width:
                    pygame.draw.line(self.surface, (70, 70, 70), (int(x), 0), (int(x), self.height), 1)

                t8 = t + seconds_per_beat / 2
                x8 = self._time_to_x(t8)
                if 0 <= x8 <= self.width:
                    pygame.draw.line(self.surface, (50, 50, 50), (int(x8), 0), (int(x8), self.height), 1)

                t16a = t + seconds_per_beat / 4
                t16b = t + 3 * seconds_per_beat / 4
                for t16 in (t16a, t16b):
                    x16 = self._time_to_x(t16)
                    if 0 <= x16 <= self.width:
                        pygame.draw.line(self.surface, (40, 40, 40), (int(x16), 0), (int(x16), self.height), 1)

    def _draw_measure_numbers(self):
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
                label = self.font.render(str(bar_index + 1), True, (220, 220, 220))
                self.surface.blit(label, (int(x) + 4, self.margin_top - 18))

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

        # Background / grid / rulers
        self._draw_timeline_ruler()
        self._draw_grid_lines()
        self._draw_measure_numbers()

        # Staff
        staff = self._render_staff_lines()
        self.surface.blit(staff, (0, 0))

        # Barlines
        self._draw_barlines()

        if not isinstance(notes, (list, tuple)):
            self._draw_playhead()
            return self.surface

        # Active track for color boost
        try:
            active_track_id = self.track_manager.get_active_track()
        except Exception:
            active_track_id = None

        # Group notes into chords (multi-head)
        grouped = self._group_notes(list(notes))

        # Precompute beat length for grouping logic
        seconds_per_beat = 60.0 / self.bpm if self.bpm > 0 else None

        # For grouping: store chord positions per track
        chord_positions: Dict[int, List[Tuple[float, float, float, float, Tuple[int, int, int]]]] = {}

        for (timestamp, track_id), chord_notes in grouped.items():
            # -------------------------------
            # MUTE / SOLO / VISIBILITY FILTER
            # -------------------------------
            try:
                if self.track_manager.solo_mode_active() and not self.track_manager.is_solo(track_id):
                    continue
                if self.track_manager.is_muted(track_id):
                    continue
            except Exception:
                pass

            try:
                if not self.track_manager.is_visible(track_id):
                    continue
            except Exception:
                pass

            # B/ – farba s podporou aktívnej stopy
            color = self._get_track_color(track_id, active_track_id)
            base_x = self._time_to_x(timestamp)

            # Sort chord notes by pitch for consistent layout
            try:
                chord_notes_sorted = sorted(
                    chord_notes,
                    key=lambda n: int(n.get("pitch") or n.get("note") or 0)
                )
            except Exception:
                chord_notes_sorted = chord_notes

            min_y = float("inf")
            max_y = float("-inf")

            # Draw multi-head chord
            for idx, note in enumerate(chord_notes_sorted):
                midi = note.get("pitch") or note.get("note")
                if midi is None:
                    continue

                try:
                    midi_int = int(midi)
                except Exception:
                    continue

                y = self._pitch_to_y(midi_int)
                x = base_x + idx * 6
                self._draw_note(self.surface, x, y, color)

                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y

            if min_y != float("inf") and max_y != float("-inf"):
                chord_positions.setdefault(track_id, []).append(
                    (timestamp, base_x, min_y, max_y, color)
                )

        # -----------------------------------------------------
        # PREMIUM STEMS
        # -----------------------------------------------------
        if seconds_per_beat is not None:
            beam_candidates: Dict[int, set] = {}
            for track_id, chords in chord_positions.items():
                if len(chords) < 2:
                    continue
                chords_sorted = sorted(chords, key=lambda c: c[0])
                for i in range(len(chords_sorted) - 1):
                    t1, _, _, _, _ = chords_sorted[i]
                    t2, _, _, _, _ = chords_sorted[i + 1]
                    dt = t2 - t1
                    if dt <= 0:
                        continue
                    if dt <= seconds_per_beat:
                        beam_candidates.setdefault(track_id, set()).add(t1)
                        beam_candidates.setdefault(track_id, set()).add(t2)

            for track_id, chords in chord_positions.items():
                for (timestamp, base_x, min_y, max_y, color) in chords:
                    staff_middle = self.margin_top + 2 * self.staff_line_spacing
                    chord_center = (min_y + max_y) / 2.0

                    stem_up = chord_center > staff_middle

                    if stem_up:
                        anchor_y = min_y
                    else:
                        anchor_y = max_y

                    base_length = 28.0

                    if track_id in beam_candidates and timestamp in beam_candidates[track_id]:
                        base_length = 35.0

                    distance_factor = min(1.5, max(0.7, abs(chord_center - staff_middle) / 40.0))
                    stem_length = base_length * distance_factor

                    start_y = anchor_y + 6
                    if stem_up:
                        end_y = start_y - stem_length
                    else:
                        end_y = start_y + stem_length

                    min_limit = self.margin_top - 30
                    max_limit = self.height - 20
                    end_y = max(min_limit, min(max_limit, end_y))

                    pygame.draw.line(
                        self.surface,
                        color,
                        (int(base_x), int(start_y)),
                        (int(base_x), int(end_y)),
                        3
                    )

        # GROUPING: BEAMS
        if seconds_per_beat is not None:
            for track_id, chords in chord_positions.items():
                if len(chords) < 2:
                    continue

                chords_sorted = sorted(chords, key=lambda c: c[0])

                for i in range(len(chords_sorted) - 1):
                    t1, x1, min_y1, max_y1, color1 = chords_sorted[i]
                    t2, x2, min_y2, max_y2, color2 = chords_sorted[i + 1]

                  
