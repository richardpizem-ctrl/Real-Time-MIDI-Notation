# graphic_renderer.py – GraphicNotationRenderer (FÁZA 4)
# Integrovaný LayerManager + RenderContext
# Bezpečný, odolný renderer pre multi-track grafickú notáciu

from typing import List, Dict, Any, Tuple, Optional
import time

try:
    import pygame
except Exception:
    pygame = None

# ------------------------------------------------------------
# LAYER SYSTEM
# ------------------------------------------------------------
from .renderer_layers import (
    LayerManager,
    GridLayer,
    NotesLayer,
    PlayheadLayer,
    MarkerLayer,
)
from .layers.timeline_layer import TimelineLayer


class RenderContext:
    """
    Kontext pre vrstvy renderera.
    Obsahuje všetky objekty, ktoré vrstvy potrebujú.
    """
    def __init__(self, timeline_controller, note_renderer, playhead, marker_renderer):
        self.timeline_controller = timeline_controller
        self.note_renderer = note_renderer
        self.playhead = playhead
        self.marker_renderer = marker_renderer


# ------------------------------------------------------------
# GRAPHIC NOTATION RENDERER
# ------------------------------------------------------------

class GraphicNotationRenderer:
    def __init__(self, width: int, height: int, track_manager, track_control=None):
        self.width = int(width)
        self.height = int(height)
        self.track_manager = track_manager
        self.track_control = track_control

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

        # Timeline
        self.timeline_height = 80
        self.timeline_controller = None

        # Tempo
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

        # Playhead
        self.playhead_x = self.width // 2

        # Color mode
        self.color_mode = "heatmap"

        # ------------------------------------------------------------
        # LAYER MANAGER
        # ------------------------------------------------------------
        self.layers = LayerManager()

        # Vrstvy pridávame v poradí kreslenia
        # 1) Timeline (grid + markers + playhead)
        if self.timeline_controller is not None:
            self.layers.add_layer(TimelineLayer(self.timeline_controller))

        # 2) Notes
        self.layers.add_layer(NotesLayer())

        # 3) Playhead overlay
        self.layers.add_layer(PlayheadLayer())

        # 4) Markers overlay
        self.layers.add_layer(MarkerLayer())

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
            if self.timeline_controller is not None:
                try:
                    self.timeline_controller.set_bpm(self.bpm)
                except Exception:
                    pass

    def set_zoom(self, zoom: float) -> None:
        try:
            z = max(0.1, min(float(zoom), 5.0))
        except Exception:
            return

        self.zoom = z

        if self.timeline_controller is not None:
            try:
                self.timeline_controller.set_zoom(self.zoom)
            except Exception:
                pass

    def set_playback_time(self, t: float) -> None:
        try:
            self.playback_time = float(t)
        except Exception:
            return

        if self.timeline_controller is not None:
            try:
                self.timeline_controller.update(self.playback_time)
            except Exception:
                pass

    def update_visibility(self, track_index: int, visible: bool) -> None:
        return

    def update_color(self, track_index: int, color_hex: str) -> None:
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

        if self.timeline_controller is not None:
            try:
                self.timeline_controller.update(self.playback_time)
                self.timeline_controller.set_scroll(self.scroll_offset)
            except Exception:
                pass

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

        reference_pitch = 60
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

    # ---------------------------------------------------------
    # MAIN RENDER
    # ---------------------------------------------------------
    def render(self):
        if pygame is None or self.surface is None:
            return None

        self._update_time()

        try:
            self.surface.fill((10, 10, 15))
        except Exception:
            return self.surface

        # STAFF
        staff_surface = self._render_staff_lines()
        if staff_surface is not None:
            try:
                self.surface.blit(staff_surface, (0, self.timeline_height))
            except Exception:
                pass

        # LAYERED RENDERING
        context = RenderContext(
            timeline_controller=self.timeline_controller,
            note_renderer=self,
            playhead=self,
            marker_renderer=self.timeline_controller,
        )

        self.layers.draw(self.surface, context)

        return self.surface
