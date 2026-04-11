"""
graphic_renderer.py – GraphicNotationRenderer (FÁZA 4)

- Bezpečný, odolný renderer pre multi-track grafickú notáciu
- Žiadne pády pri chýbajúcom pygame, fonte, track_manageri alebo track_control
- Bezpečné výpočty času, pozícií, farieb a skupín akordov
- Pripravené na integráciu s UIManager, TrackControlManager a TrackManager
"""

from typing import List, Dict, Any, Tuple, Optional

import time

try:
    import pygame
except Exception:
    pygame = None


class GraphicNotationRenderer:
    def __init__(self, width: int, height: int, track_manager, track_control=None):
        self.width = int(width)
        self.height = int(height)
        self.track_manager = track_manager
        self.track_control = track_control  # optional TrackControlManager

        # Surface
        if pygame is not None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                self.surface = None
        else:
            self.surface = None

        # Font
        if pygame is not None:
            try:
                self.font = pygame.font.SysFont("Arial", 18)
            except Exception:
                self.font = None
        else:
            self.font = None

        # Staff cache
        self.staff_cache = None
        self.staff_cache_width = self.width
        self.staff_cache_height = 140

        # Layout
        self.margin_left = 40
        self.margin_top = 20
        self.staff_line_spacing = 12

        # Multi-track lane height
        self.track_lane_height = 22.0

        # Playback
        self.playback_time = 0.0
        self.last_frame_time = time.time()

        # View
        self.zoom = 1.0
        self.scroll_speed = 120.0
        self.scroll_offset = 0.0

        # Tempo
        self.bpm = 120.0
        self.beats_per_bar = 4

        # Playhead
        self.playhead_x = self.width // 2

        # Color mode
        self.color_mode = "heatmap"

    # ---------------------------------------------------------
    # TRACK LANE OFFSET
    # ---------------------------------------------------------
    def _track_lane_offset(self, track_id: int) -> float:
        try:
            tid = int(track_id)
        except Exception:
            tid = 1
        return (tid - 1) * self.track_lane_height

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def set_color_mode(self, mode: str) -> None:
        if mode in ("classic", "heatmap", "glow"):
            self.color_mode = mode

    def set_bpm(self, bpm: float) -> None:
        try:
            b = float(bpm)
        except Exception:
            return
        if b > 0:
            self.bpm = b

    def set_playback_time(self, t: float) -> None:
        try:
            self.playback_time = float(t)
        except Exception:
            pass

    def update_visibility(self, track_index: int, visible: bool) -> None:
        """
        Volané z UIManager._on_visibility_changed.
        Viditeľnosť je riadená TrackControlManagerom / TrackManagerom.
        Renderer stav len číta – žiadny lokálny cache.
        """
        return

    def update_color(self, track_index: int, color_hex: str) -> None:
        """
        Volané z UIManager._on_color_changed.
        Farby renderer číta dynamicky z TrackControlManager / TrackManager.
        """
        return

    # ---------------------------------------------------------
    # TIME UPDATE
    # ---------------------------------------------------------
    def _update_time(self) -> None:
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now

        if dt < 0:
            dt = 0.0

        self.playback_time += dt
        self.scroll_offset += self.scroll_speed * dt

    # ---------------------------------------------------------
    # TIME → X
    # ---------------------------------------------------------
    def _time_to_x(self, t: float) -> float:
        try:
            tt = float(t)
        except Exception:
            tt = self.playback_time

        if self.bpm <= 0:
            pixels_per_second = 80.0 * self.zoom
        else:
            seconds_per_beat = 60.0 / self.bpm
            pixels_per_beat = 80.0 * self.zoom
            pixels_per_second = pixels_per_beat / seconds_per_beat

        dt = tt - self.playback_time
        x = self.playhead_x + dt * pixels_per_second - self.scroll_offset
        return x

    # ---------------------------------------------------------
    # PITCH → Y
    # ---------------------------------------------------------
    def _pitch_to_y(self, midi: int, track_id: int) -> float:
        try:
            midi_int = int(midi)
        except Exception:
            midi_int = 60

        reference_pitch = 60  # C4
        staff_center = self.margin_top + 2 * self.staff_line_spacing
        semitone_step = self.staff_line_spacing / 2.0

        dy = (reference_pitch - midi_int) * semitone_step
        y = staff_center + dy

        y += self._track_lane_offset(track_id)
        return y

    # ---------------------------------------------------------
    # STAFF LINES (cached)
    # ---------------------------------------------------------
    def _render_staff_lines(self):
        if pygame is None:
            return None

        if (
            self.staff_cache is not None
            and self.staff_cache.get_width() == self.staff_cache_width
            and self.staff_cache.get_height() == self.staff_cache_height
        ):
            return self.staff_cache

        try:
            staff_surface = pygame.Surface(
                (self.staff_cache_width, self.staff_cache_height),
                pygame.SRCALPHA
            )
        except Exception:
            return None

        staff_surface.fill((0, 0, 0, 0))

        for i in range(5):
            y = self.margin_top + i * self.staff_line_spacing
            try:
                pygame.draw.line(
                    staff_surface,
                    (200, 200, 200),
                    (self.margin_left, int(y)),
                    (self.staff_cache_width - 20, int(y)),
                    2,
                )
            except Exception:
                continue

        self.staff_cache = staff_surface
        return self.staff_cache

    # ---------------------------------------------------------
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _hex_to_rgb(self, h: str) -> Tuple[int, int, int]:
        if not isinstance(h, str):
            return (120, 180, 220)
        h = h.lstrip("#")
        if len(h) != 6:
            return (120, 180, 220)
        try:
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except Exception:
            return (120, 180, 220)

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lerp(self, a: float, b: float, t: float) -> float:
        return a + (b - a) * t

    def _mix_colors(
        self,
        c1: Tuple[int, int, int],
        c2: Tuple[int, int, int],
        t: float
    ) -> Tuple[int, int, int]:
        t = max(0.0, min(1.0, float(t)))
        r = int(self._lerp(c1[0], c2[0], t))
        g = int(self._lerp(c1[1], c2[1], t))
        b = int(self._lerp(c1[2], c2[2], t))
        return (r, g, b)

    def _velocity_to_color(
        self,
        base_color: Tuple[int, int, int],
        velocity: int
    ) -> Tuple[int, int, int]:
        try:
            v = int(velocity)
        except Exception:
            v = 100

        v = max(1, min(127, v))
        t = v / 127.0

        if self.color_mode == "classic":
            factor = 0.4 + 0.6 * t
            return (
                int(base_color[0] * factor),
                int(base_color[1] * factor),
                int(base_color[2] * factor),
            )

        blue = (0x4D, 0xA6, 0xFF)
        green = (0x33, 0xCC, 0x33)
        red = (0xFF, 0x44, 0x44)

        if t <= 0.5:
            lt = t / 0.5
            r = int(self._lerp(blue[0], green[0], lt))
            g = int(self._lerp(blue[1], green[1], lt))
            b = int(self._lerp(blue[2], green[2], lt))
        else:
            lt = (t - 0.5) / 0.5
            r = int(self._lerp(green[0], red[0], lt))
            g = int(self._lerp(green[1], red[1], lt))
            b = int(self._lerp(green[2], red[2], lt))

        color = (r, g, b)

        if self.color_mode == "glow":
            color = self._mix_colors(color, (255, 255, 255), 0.35)

        return color

    # ---------------------------------------------------------
    # VELOCITY FACTOR
    # ---------------------------------------------------------
    def _velocity_factor(self, velocity: int) -> float:
        try:
            v = int(velocity)
        except Exception:
            return 1.0
        return max(0.3, min(1.0, v / 127.0))

    # ---------------------------------------------------------
    # DRAW NOTE
    # ---------------------------------------------------------
    def _draw_note(
        self,
        surface,
        x: float,
        y: float,
        base_color: Tuple[int, int, int],
        velocity: int,
        flash: float = 0.0
    ) -> None:
        if pygame is None or surface is None:
            return

        factor = self._velocity_factor(velocity)
        color = self._velocity_to_color(base_color, velocity)

        try:
            f = float(flash)
        except Exception:
            f = 0.0

        if f > 0.01:
            color = self._mix_colors(color, (255, 255, 255), min(0.8, f))

        w = int(16 * (0.8 + 0.4 * factor))
        h = int(12 * (0.8 + 0.4 * factor))

        rect = pygame.Rect(int(x), int(y), w, h)
        try:
            pygame.draw.ellipse(surface, color, rect)
            outline = int(1 + factor * 2)
            pygame.draw.ellipse(surface, (0, 0, 0), rect, outline)
        except Exception:
            pass

    # ---------------------------------------------------------
    # LIGATURE / SIMPLE BEAM
    # ---------------------------------------------------------
    def _draw_ligature(self, x1, x2, y, color) -> None:
        if pygame is None or self.surface is None:
            return
        try:
            pygame.draw.line(
                self.surface,
                color,
                (int(x1), int(y)),
                (int(x2), int(y)),
                4
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # BEAM DRAWING
    # ---------------------------------------------------------
    def _draw_beam(self, x1, y1, x2, y2, color, levels=1) -> None:
        if pygame is None or self.surface is None:
            return
        try:
            lv = max(1, int(levels))
        except Exception:
            lv = 1

        for level in range(lv):
            offset = level * 4
            try:
                pygame.draw.line(
                    self.surface,
                    color,
                    (int(x1), int(y1 - offset)),
                    (int(x2), int(y2 - offset)),
                    3
                )
            except Exception:
                continue

    # ---------------------------------------------------------
    # CHORD GROUPING
    # ---------------------------------------------------------
    def _group_notes(self, notes: List[Dict[str, Any]]):
        groups: Dict[Tuple[float, int], List[Dict[str, Any]]] = {}
        time_quantum = 0.02

        if not isinstance(notes, (list, tuple)):
            return groups

        for note in notes:
            if not isinstance(note, dict):
                continue

            midi = note.get("pitch")
            if midi is None:
                midi = note.get("note")

            track_id = note.get("track_id")
            timestamp = note.get("timestamp", 0.0)

            if midi is None or track_id is None:
                continue

            try:
                t = float(timestamp)
            except Exception:
                t = 0.0

            try:
                tid = int(track_id)
            except Exception:
                continue

            quantized_time = round(t / time_quantum) * time_quantum
            key = (quantized_time, tid)
            groups.setdefault(key, []).append(note)

        return groups

    # ---------------------------------------------------------
    # BARLINES / GRID / RULER
    # ---------------------------------------------------------
    def _draw_barlines(self) -> None:
        if pygame is None or self.surface is None:
            return
        if self.bpm <= 0 or self.beats_per_bar <= 0:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar = int(self.playback_time // seconds_per_bar)
        bars = range(current_bar - 4, current_bar + 12)

        for bar in bars:
            if bar < 0:
                continue

            bar_time = bar * seconds_per_bar
            x = self._time_to_x(bar_time)

            if 0 <= x <= self.width:
                try:
                    pygame.draw.line(
                        self.surface,
                        (255, 255, 180),
                        (int(x), 0),
                        (int(x), self.height),
                        3
                    )
                except Exception:
                    continue

    def _draw_timeline_ruler(self) -> None:
        if pygame is None or self.surface is None:
            return
        if self.bpm <= 0 or self.beats_per_bar <= 0 or self.font is None:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar = int(self.playback_time // seconds_per_bar)
        bars = range(current_bar - 4, current_bar + 12)

        for bar in bars:
            if bar < 0:
                continue

            bar_time = bar * seconds_per_bar
            x = self._time_to_x(bar_time)

            if 0 <= x <= self.width:
                try:
                    label = self.font.render(str(bar + 1), True, (230, 230, 230))
                    self.surface.blit(label, (int(x) + 4, 0))
                except Exception:
                    continue

    def _draw_grid_lines(self) -> None:
        if pygame is None or self.surface is None:
            return
        if self.bpm <= 0 or self.beats_per_bar <= 0:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar = int(self.playback_time // seconds_per_bar)
        bars = range(current_bar - 4, current_bar + 12)

        for bar in bars:
            if bar < 0:
                continue

            bar_start = bar * seconds_per_bar

            for beat in range(self.beats_per_bar):
                t = bar_start + beat * seconds_per_beat
                x = self._time_to_x(t)

                if 0 <= x <= self.width:
                    try:
                        pygame.draw.line(
                            self.surface,
                            (70, 70, 70),
                            (int(x), 0),
                            (int(x), self.height),
                            1
                        )
                    except Exception:
                        pass

                # 8th
                t8 = t + seconds_per_beat / 2
                x8 = self._time_to_x(t8)
                if 0 <= x8 <= self.width:
                    try:
                        pygame.draw.line(
                            self.surface,
                            (50, 50, 50),
                            (int(x8), 0),
                            (int(x8), self.height),
                            1
                        )
                    except Exception:
                        pass

                # 16th
                t16a = t + seconds_per_beat / 4
                t16b = t + 3 * seconds_per_beat / 4
                for t16 in (t16a, t16b):
                    x16 = self._time_to_x(t16)
                    if 0 <= x16 <= self.width:
                        try:
                            pygame.draw.line(
                                self.surface,
                                (40, 40, 40),
                                (int(x16), 0),
                                (int(x16), self.height),
                                1
                            )
                        except Exception:
                            pass

    def _draw_measure_numbers(self) -> None:
        if pygame is None or self.surface is None:
            return
        if self.bpm <= 0 or self.beats_per_bar <= 0 or self.font is None:
            return

        seconds_per_beat = 60.0 / self.bpm
        seconds_per_bar = seconds_per_beat * self.beats_per_bar

        current_bar = int(self.playback_time // seconds_per_bar)
        bars = range(current_bar - 4, current_bar + 12)

        for bar in bars:
            if bar < 0:
                continue

            bar_time = bar * seconds_per_bar
            x = self._time_to_x(bar_time)

            if 0 <= x <= self.width:
                try:
                    label = self.font.render(str(bar + 1), True, (220, 220, 220))
                    self.surface.blit(label, (int(x) + 4, self.margin_top - 18))
                except Exception:
                    continue

    # ---------------------------------------------------------
    # PLAYHEAD
    # ---------------------------------------------------------
    def _draw_playhead(self) -> None:
        if pygame is None or self.surface is None:
            return
        try:
            pygame.draw.line(
                self.surface,
                (255, 80, 80),
                (int(self.playhead_x), 0),
                (int(self.playhead_x), self.height),
                3
            )
        except Exception:
            pass

    # ---------------------------------------------------------
    # TRACK COLOR
    # ---------------------------------------------------------
    def _get_track_color(self, track_id: int, active_track_id: Optional[int]):
        base_color = (120, 180, 220)

        # TrackControlManager (indexované od 0)
        if self.track_control is not None:
            try:
                hex_color = self.track_control.get_color(track_id - 1)
                base_color = self._hex_to_rgb(hex_color)
            except Exception:
                pass
        else:
            # TrackManager (môže vracať RGB tuple)
            try:
                c = self.track_manager.get_color(track_id)
                if isinstance(c, (list, tuple)) and len(c) == 3:
                    base_color = (int(c[0]), int(c[1]), int(c[2]))
            except Exception:
                pass

        if active_track_id is not None and track_id == active_track_id:
            r = min(255, int(base_color[0] * 1.1))
            g = min(255, int(base_color[1] * 1.1))
            b = min(255, int(base_color[2] * 1.1))
            return (r, g, b)

        return base_color

    # ---------------------------------------------------------
    # MAIN DRAW
    # ---------------------------------------------------------
    def draw(self, notes):
        if pygame is None:
            return None

        if self.surface is None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                return None

        self._update_time()
        try:
            self.surface.fill((25, 25, 25))
        except Exception:
            pass

        # Background layers
        self._draw_timeline_ruler()
        self._draw_grid_lines()
        self._draw_measure_numbers()

        staff = self._render_staff_lines()
        if staff is not None:
            try:
                self.surface.blit(staff, (0, 0))
            except Exception:
                pass

        self._draw_barlines()

        if not isinstance(notes, (list, tuple)):
            self._draw_playhead()
            return self.surface

        # Active track
        active_track_id: Optional[int]
        try:
            if self.track_control is not None:
                at = self.track_control.get_active_track()
                active_track_id = int(at) + 1
            else:
                at = self.track_manager.get_active_track()
                active_track_id = int(at)
        except Exception:
            active_track_id = None

        grouped = self._group_notes(list(notes))

        seconds_per_beat = 60.0 / self.bpm if self.bpm > 0 else None

        chord_positions: Dict[int, List[Tuple[float, float, float, float, Tuple[int, int, int]]]] = {}
        activity_accumulator = {i: 0.0 for i in range(1, 17)}

        # ---------------------------------------------------------
        # DRAW CHORDS
        # ---------------------------------------------------------
        for (timestamp, track_id), chord_notes in grouped.items():
            # Track effectively active?
            try:
                if hasattr(self.track_manager, "is_effectively_active"):
                    if not self.track_manager.is_effectively_active(track_id):
                        continue
            except Exception:
                pass

            # Visibility
            visible = True
            if self.track_control is not None:
                try:
                    visible = self.track_control.is_visible(track_id - 1)
                except Exception:
                    pass
            else:
                try:
                    if hasattr(self.track_manager, "is_visible"):
                        visible = self.track_manager.is_visible(track_id)
                except Exception:
                    pass

            if not visible:
                continue

            base_color = self._get_track_color(track_id, active_track_id)

            # Volume
            try:
                vol = float(self.track_manager.get_volume(track_id))
                vol = max(0.0, min(1.0, vol))
            except Exception:
                vol = 1.0

            vr = int(base_color[0] * (0.4 + 0.6 * vol))
            vg = int(base_color[1] * (0.4 + 0.6 * vol))
            vb = int(base_color[2] * (0.4 + 0.6 * vol))
            track_color = (vr, vg, vb)

            base_x = self._time_to_x(timestamp)

            try:
                chord_sorted = sorted(
                    chord_notes,
                    key=lambda n: int(n.get("pitch") or n.get("note") or 0)
                )
            except Exception:
                chord_sorted = chord_notes

            min_y = float("inf")
            max_y = float("-inf")

            for idx, note in enumerate(chord_sorted):
                midi = note.get("pitch")
                if midi is None:
                    midi = note.get("note")

                velocity = note.get("velocity", 100)

                if midi is None:
                    continue

                try:
                    midi_int = int(midi)
                except Exception:
                    continue

                y = self._pitch_to_y(midi_int, track_id)
                x = base_x + idx * 6

                flash = note.get("_flash", 1.0)
                self._draw_note(self.surface, x, y, track_color, velocity, flash)

                try:
                    note["_flash"] = float(flash) * 0.85
                except Exception:
                    note["_flash"] = 0.0

                if track_id in activity_accumulator:
                    try:
                        activity_accumulator[track_id] += float(velocity) / 127.0
                    except Exception:
                        pass

                min_y = min(min_y, y)
                max_y = max(max_y, y)

            if min_y != float("inf"):
                chord_positions.setdefault(track_id, []).append(
                    (float(timestamp), base_x, min_y, max_y, track_color)
                )

        # ---------------------------------------------------------
        # UPDATE TRACK ACTIVITY
        # ---------------------------------------------------------
        for tid, val in activity_accumulator.items():
            level = min(1.0, max(0.0, val))
            try:
                if hasattr(self.track_manager, "update_activity"):
                    self.track_manager.update_activity(tid, level)
            except Exception:
                pass

        # ---------------------------------------------------------
        # STEMS
        # ---------------------------------------------------------
        if seconds_per_beat is not None:
            beam_candidates: Dict[int, set] = {}

            for track_id, chords in chord_positions.items():
                if len(chords) < 2:
                    continue

                chords_sorted = sorted(chords, key=lambda c: c[0])

                for i in range(len(chords_sorted) - 1):
                    t1 = chords_sorted[i][0]
                    t2 = chords_sorted[i + 1][0]
                    dt = t2 - t1

                    if 0 < dt <= seconds_per_beat:
                        beam_candidates.setdefault(track_id, set()).add(t1)
                        beam_candidates.setdefault(track_id, set()).add(t2)

            for track_id, chords in chord_positions.items():
                for (timestamp, base_x, min_y, max_y, color) in chords:
                    staff_mid = self.margin_top + 2 * self.staff_line_spacing
                    chord_mid = (min_y + max_y) / 2.0

                    stem_up = chord_mid > staff_mid
                    anchor_y = min_y if stem_up else max_y

                    base_len = 28.0
                    if track_id in beam_candidates and timestamp in beam_candidates[track_id]:
                        base_len = 35.0

                    dist_factor = min(1.5, max(0.7, abs(chord_mid - staff_mid) / 40.0))
                    stem_len = base_len * dist_factor

                    start_y = anchor_y + 6
                    end_y = start_y - stem_len if stem_up else start_y + stem_len
                    end_y = max(self.margin_top - 30, min(self.height - 20, end_y))

                    try:
                        pygame.draw.line(
                            self.surface,
                            color,
                            (int(base_x), int(start_y)),
                            (int(base_x), int(end_y)),
                            3
                        )
                    except Exception:
                        pass

        # ---------------------------------------------------------
        # BEAMS
        # ---------------------------------------------------------
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

        # ---------------------------------------------------------
        # PLAYHEAD
        # ---------------------------------------------------------
        self._draw_playhead()
        return self.surface
