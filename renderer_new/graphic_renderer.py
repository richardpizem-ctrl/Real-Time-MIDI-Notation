# graphic_renderer.py – GraphicNotationRenderer (FÁZA 4)
# Bezpečný, odolný renderer pre multi-track grafickú notáciu
# Žiadne pády pri chýbajúcom pygame, fonte, track_manageri alebo track_control
# Bezpečné výpočty času, pozícií, farieb a skupín akordov
# Pripravené na integráciu s UIManager, TrackControlManager a TrackManager

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

        # Timeline (hore nad notami)
        self.timeline_height = 80
        self.timeline_controller = None
        if pygame is not None:
            try:
                from .timeline_controller import TimelineController
                self.timeline_controller = TimelineController(
                    width=self.width,
                    height=self.timeline_height,
                    bpm=120.0,
                )
            except Exception:
                self.timeline_controller = None

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
    # PUBLIC API (ZJEDNOTENÉ S UIMANAGER)
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
        Renderer viditeľnosť necache-uje – číta ju dynamicky.
        """
        return

    def update_color(self, track_index: int, color_hex: str) -> None:
        """
        Volané z UIManager._on_color_changed.
        Renderer farby necache-uje – číta ich dynamicky.
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
        staff_center = self.timeline_height + self.margin_top + 2 * self.staff_line_spacing
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
                        (int(x), self.timeline_height),
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
                    self.surface.blit(label, (int(x) + 4, self.timeline_height))
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
                            (int(x), self.timeline_height),
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
                            (int(x8), self.timeline_height),
                            (int(x8), self.height),
                            1
                        )
                    except Exception:
                        pass

                # 16th
                t16a = t + seconds_per_beat / 4
                t16b = t + 3 * seconds_per_beat / 4
                for t16 in (t16a, t16b):
                    x16 = self._time_to_x
