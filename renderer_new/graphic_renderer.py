# =========================================================
# GraphicNotationRenderer v2.0.0
# Stabilný renderer pre multi‑track grafickú notáciu
# Integrovaný LayerManager + RenderContext
# =========================================================

from typing import List, Dict, Any, Tuple, Optional
import time

try:
    import pygame
except Exception:
    pygame = None

# ------------------------------------------------------------
# LAYER SYSTEM – tvoje reálne vrstvy
# ------------------------------------------------------------
from .layers import LayerManager
from .layers.timeline_layer import TimelineLayer
from .selection_layer import SelectionLayer


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
    """
    GraphicNotationRenderer (v2.0.0)
    - stabilný
    - real‑time safe
    - kompatibilný s TimelineController
    - používa LayerManager
    - pripravený na v3 (AI/TIMELINE)
    """

    def __init__(self, width: int, height: int, track_manager, track_control=None):
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

        # TimelineController
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
        # LAYER MANAGER – tvoje reálne vrstvy
        # ------------------------------------------------------------
        self.layers = LayerManager()

        # 1) Timeline (grid + markers + playhead)
        if self.timeline_controller is not None:
            self.layers.add_layer(TimelineLayer(self.timeline_controller))

        # 2) Selection overlay (výber nôt)
        self.layers.add_layer(SelectionLayer(self.timeline_controller))

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
                self.timeline_controller.set_offset(self.scroll_offset)
            except Exception:
                pass

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

        try:
            self.layers.render(self.surface)
        except Exception:
            pass

        return self.surface
