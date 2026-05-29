# =========================================================
# GraphicNotationRenderer v4.3.0
# Výkonnostná + diagnostická verzia
# - mikrooptimalizácie
# - partial redraw
# - staff cache optimalizácia
# - real‑time profiling hook
# =========================================================

from typing import Optional
import time

try:
    import pygame
except Exception:
    pygame = None

from .layers import LayerManager
from .layers.timeline_layer import TimelineLayer
from .selection_layer import SelectionLayer


# ------------------------------------------------------------
# PROFILER (lightweight)
# ------------------------------------------------------------
class RenderProfiler:
    """Ultra‑ľahký profiler pre v4.3.0."""
    def __init__(self):
        self.last_frame_ms = 0.0
        self.frame_times = []  # posledných 60 frameov

    def begin(self):
        self._start = time.perf_counter()

    def end(self):
        dt = (time.perf_counter() - self._start) * 1000.0
        self.last_frame_ms = dt
        self.frame_times.append(dt)
        if len(self.frame_times) > 60:
            self.frame_times.pop(0)


# ------------------------------------------------------------
# RENDER CONTEXT
# ------------------------------------------------------------
class RenderContext:
    def __init__(self, timeline_controller, note_renderer, playhead, marker_renderer):
        self.timeline_controller = timeline_controller
        self.note_renderer = note_renderer
        self.playhead = playhead
        self.marker_renderer = marker_renderer


# ------------------------------------------------------------
# GRAPHIC NOTATION RENDERER
# ------------------------------------------------------------
class GraphicNotationRenderer:
    """
    GraphicNotationRenderer (v4.3.0)
    - optimalizovaný
    - real‑time safe
    - partial redraw pripravené
    - diagnostika + profiler
    """

    def __init__(self, width: int, height: int, track_manager, track_control=None):
        # ------------------------------------------------------------
        # DIMENSIONS
        # ------------------------------------------------------------
        try:
            self.width = int(width)
        except Exception:
            self.width = 1600

        try:
            self.height = int(height)
        except Exception:
            self.height = 400

        self.track_manager = track_manager
        self.track_control = track_control

        # ------------------------------------------------------------
        # SURFACE
        # ------------------------------------------------------------
        if pygame is not None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                self.surface = None
        else:
            self.surface = None

        # ------------------------------------------------------------
        # FONT
        # ------------------------------------------------------------
        if pygame is not None:
            try:
                self.font = pygame.font.SysFont("Arial", 18)
            except Exception:
                self.font = None
        else:
            self.font = None

        # ------------------------------------------------------------
        # TIMELINE CONTROLLER
        # ------------------------------------------------------------
        self.timeline_height = 80
        self.timeline_controller = None

        self.bpm = 120.0
        self.beats_per_bar = 4

        if pygame is not None:
            try:
                from .timeline_controller import TimelineController
                self.timeline_controller = TimelineController(
                    width=self.width,
                    height=self.timeline_height,
                    bpm=self.bpm,
                    beats_per_bar=self.beats_per_bar,
                    pixels_per_beat=100,
                )
            except Exception:
                self.timeline_controller = None

        # ------------------------------------------------------------
        # STAFF CACHE
        # ------------------------------------------------------------
        self.staff_cache = None
        self.staff_cache_width = self.width
        self.staff_cache_height = 140

        self.margin_left = 40
        self.margin_top = 20
        self.staff_line_spacing = 12

        # ------------------------------------------------------------
        # TRACK LANE
        # ------------------------------------------------------------
        self.track_lane_height = 22.0

        # ------------------------------------------------------------
        # PLAYBACK
        # ------------------------------------------------------------
        self.playback_time = 0.0
        self.last_frame_time = time.time()

        # ------------------------------------------------------------
        # VIEW
        # ------------------------------------------------------------
        self.zoom = 1.0
        self.scroll_speed = 120.0
        self.scroll_offset = 0.0
        self.playhead_x = self.width // 2

        # ------------------------------------------------------------
        # COLOR MODE
        # ------------------------------------------------------------
        self.color_mode = "heatmap"

        # ------------------------------------------------------------
        # LAYERS
        # ------------------------------------------------------------
        self.layers = LayerManager()

        if self.timeline_controller is not None:
            self.layers.add_layer(TimelineLayer(self.timeline_controller))

        self.layers.add_layer(SelectionLayer(self.timeline_controller))

        # ------------------------------------------------------------
        # PROFILER
        # ------------------------------------------------------------
        self.profiler = RenderProfiler()

    # ---------------------------------------------------------
    # TRACK LANE OFFSET
    # ---------------------------------------------------------
    def _track_lane_offset(self, track_id: int) -> float:
        try:
            return (int(track_id) - 1) * self.track_lane_height
        except Exception:
            return 0.0

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
            if self.timeline_controller:
                try:
                    self.timeline_controller.set_bpm(b)
                except Exception:
                    pass

    def set_zoom(self, zoom: float) -> None:
        try:
            z = max(0.1, min(float(zoom), 5.0))
        except Exception:
            return

        self.zoom = z

        if self.timeline_controller:
            try:
                self.timeline_controller.set_zoom(z)
            except Exception:
                pass

    def set_playback_time(self, t: float) -> None:
        try:
            self.playback_time = float(t)
        except Exception:
            return

        if self.timeline_controller:
            try:
                self.timeline_controller.update(self.playback_time)
            except Exception:
                pass

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

        if self.timeline_controller:
            try:
                self.timeline_controller.update(self.playback_time)
                self.timeline_controller.set_offset(self.scroll_offset)
            except Exception:
                pass

    # ---------------------------------------------------------
    # STAFF LINES (cached)
    # ---------------------------------------------------------
    def _render_staff_lines(self):
        if pygame is None:
            return None

        # cache hit
        if (
            self.staff_cache is not None
            and self.staff_cache.get_width() == self.staff_cache_width
            and self.staff_cache.get_height() == self.staff_cache_height
        ):
            return self.staff_cache

        # rebuild cache
        try:
            surf = pygame.Surface(
                (self.staff_cache_width, self.staff_cache_height),
                pygame.SRCALPHA
            )
        except Exception:
            return None

        surf.fill((0, 0, 0, 0))

        draw_line = pygame.draw.line
        ml = self.margin_left
        end_x = self.staff_cache_width - 20
        mt = self.margin_top
        spacing = self.staff_line_spacing

        for i in range(5):
            y = int(mt + i * spacing)
            try:
                draw_line(surf, (200, 200, 200), (ml, y), (end_x, y), 2)
            except Exception:
                continue

        self.staff_cache = surf
        return surf

    # ---------------------------------------------------------
    # MAIN RENDER
    # ---------------------------------------------------------
    def render(self):
        if pygame is None or self.surface is None:
            return None

        self.profiler.begin()
        self._update_time()

        try:
            self.surface.fill((10, 10, 15))
        except Exception:
            return self.surface

        # STAFF
        staff_surface = self._render_staff_lines()
        if staff_surface:
            try:
                self.surface.blit(staff_surface, (0, self.timeline_height))
            except Exception:
                pass

        # CONTEXT
        context = RenderContext(
            timeline_controller=self.timeline_controller,
            note_renderer=self,
            playhead=self,
            marker_renderer=self.timeline_controller,
        )

        # LAYERS
        try:
            self.layers.render(self.surface)
        except Exception:
            pass

        self.profiler.end()
        return self.surface
