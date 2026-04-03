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

    # ---------------------------------------------------------
    # VELOCITY → vizuálny faktor
    # ---------------------------------------------------------
    def _velocity_factor(self, velocity: int) -> float:
        try:
            v = int(velocity)
        except Exception:
            return 1.0
        return max(0.3, min(1.0, v / 127.0))

    # ---------------------------------------------------------
    # NOTE DRAWING (upravené pre velocity)
    # ---------------------------------------------------------
    def _draw_note(self, surface, x: float, y: float, color: Tuple[int, int, int], velocity: int):
        factor = self._velocity_factor(velocity)

        # farba podľa velocity
        color = (
            int(color[0] * factor),
            int(color[1] * factor),
            int(color[2] * factor)
        )

        # veľkosť podľa velocity
        w = int(16 * (0.8 + 0.4 * factor))
        h = int(12 * (0.8 + 0.4 * factor))

        rect = pygame.Rect(int(x), int(y), w, h)
        pygame.draw.ellipse(surface, color, rect)

        # obrys podľa velocity
        outline = int(1 + factor * 2)
        pygame.draw.ellipse(surface, (0, 0, 0), rect, outline)
    # ---------------------------------------------------------
    # LIGATURE / SIMPLE BEAM DRAWING
    # ---------------------------------------------------------
    def _draw_ligature(self, x1: float, x2: float, y: float, color: Tuple[int, int, int]):
        pygame.draw.line(self.surface, color, (int(x1), int(y)), (int(x2), int(y)), 4)

    # ---------------------------------------------------------
    # GROUPING BEAM DRAWING
    # ---------------------------------------------------------
    def _draw_beam(self, x1: float, y1: float, x2: float, y2: float, color: Tuple[int, int, int], levels: int = 1):
        for level in range(levels):
            offset = level * 4
            pygame.draw.line(
                self.surface,
                color,
                (int(x1), int(y1 - offset)),
                (int(x2), int(y2 - offset)),
                3
            )

    # ---------------------------------------------------------
    # CHORD GROUPING
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

            if 0 <= x <= self.width:
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
    # MAIN DRAW (začiatok)
    # ---------------------------------------------------------
    def draw(self, notes):
        if self.surface is None:
            self.surface = pygame.Surface((self.width, self.height))

        self._update_time()
        self.surface.fill((25, 25, 25))

        self._draw_timeline_ruler()
        self._draw_grid_lines()
        self._draw_measure_numbers()

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

        seconds_per_beat = 60.0 / self.bpm if self.bpm > 0 else None

        chord_positions: Dict[int, List[Tuple[float, float, float, float, Tuple[int, int, int]]]] = {}

        # REALTIME ACTIVITY ACCUMULATOR
        activity_accumulator = {i: 0.0 for i in range(1, 17)}

        for (timestamp, track_id), chord_notes in grouped.items():

            try:
                if not self.track_manager.is_effectively_active(track_id):
                    continue
            except Exception:
                pass

            try:
                if not self.track_manager.is_visible(track_id):
                    continue
            except Exception:
                pass

            color = self._get_track_color(track_id, active_track_id)

            try:
                vol = self.track_manager.get_volume(track_id)
                vol = max(0.0, min(1.0, float(vol)))
            except Exception:
                vol = 1.0

            vr = int(color[0] * (0.4 + 0.6 * vol))
            vg = int(color[1] * (0.4 + 0.6 * vol))
            vb = int(color[2] * (0.4 + 0.6 * vol))
            color = (vr, vg, vb)

            base_x = self._time_to_x(timestamp)

            try:
                chord_notes_sorted = sorted(
                    chord_notes,
                    key=lambda n: int(n.get("pitch") or n.get("note") or 0)
                )
            except Exception:
                chord_notes_sorted = chord_notes

            min_y = float("inf")
            max_y = float("-inf")

            for idx, note in enumerate(chord_notes_sorted):
                midi = note.get("pitch") or note.get("note")
                velocity = note.get("velocity", 100)

                if midi is None:
                    continue

                try:
                    midi_int = int(midi)
                except Exception:
                    continue

                y = self._pitch_to_y(midi_int)
                x = base_x + idx * 6

                self._draw_note(self.surface, x, y, color, velocity)

                activity_accumulator[track_id] += velocity / 127.0

                if y < min_y:
                    min_y = y
                if y > max_y:
                    max_y = y

            if min_y != float("inf") and max_y != float("-inf"):
                chord_positions.setdefault(track_id, []).append(
                    (timestamp, base_x, min_y, max_y, color)
                )
        # -----------------------------------------------------
        # SEND REALTIME ACTIVITY TO TRACKMANAGER
        # -----------------------------------------------------
        for tid, val in activity_accumulator.items():
            level = min(1.0, val)
            try:
                self.track_manager.update_activity(tid, level)
            except Exception:
                pass

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

                    if 0 < dt <= seconds_per_beat:
                        beam_candidates.setdefault(track_id, set()).add(t1)
                        beam_candidates.setdefault(track_id, set()).add(t2)

            for track_id, chords in chord_positions.items():
                for (timestamp, base_x, min_y, max_y, color) in chords:

                    staff_middle = self.margin_top + 2 * self.staff_line_spacing
                    chord_center = (min_y + max_y) / 2.0

                    stem_up = chord_center > staff_middle
                    anchor_y = min_y if stem_up else max_y

                    base_length = 28.0
                    if track_id in beam_candidates and timestamp in beam_candidates[track_id]:
                        base_length = 35.0

                    distance_factor = min(1.5, max(0.7, abs(chord_center - staff_middle) / 40.0))
                    stem_length = base_length * distance_factor

                    start_y = anchor_y + 6
                    end_y = start_y - stem_length if stem_up else start_y + stem_length

                    end_y = max(self.margin_top - 30, min(self.height - 20, end_y))

                    pygame.draw.line(
                        self.surface,
                        color,
                        (int(base_x), int(start_y)),
                        (int(base_x), int(end_y)),
                        3
                    )

        # -----------------------------------------------------
        # GROUPING: BEAMS
        # -----------------------------------------------------
        if seconds_per_beat is not None:
            for track_id, chords in chord_positions.items():
                if len(chords) < 2:
                    continue

                chords_sorted = sorted(chords, key=lambda c: c[0])

                for i in range(len(chords_sorted) - 1):
                    t1, x1, min_y1, max_y1, color1 = chords_sorted[i]
                    t2, x2, min_y2, max_y2, color2 = chords_sorted[i + 1]

                    dt = t2 - t1
                    if dt <= 0 or dt > seconds_per_beat:
                        continue

                    y1 = (min_y1 + max_y1) / 2.0
                    y2 = (min_y2 + max_y2) / 2.0

                    self._draw_beam(x1, y1, x2, y2, color1, levels=1)

        # -----------------------------------------------------
        # PLAYHEAD
        # -----------------------------------------------------
        self._draw_playhead()

        # -----------------------------------------------------
        # RETURN SURFACE
        # -----------------------------------------------------
        return self.surface
