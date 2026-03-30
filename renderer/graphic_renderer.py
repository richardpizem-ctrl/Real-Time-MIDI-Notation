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

        self.staff_cache = None
        self.staff_cache_width = width
        self.staff_cache_height = 140

        self.margin_left = 40
        self.margin_top = 20
        self.staff_line_spacing = 12

        # Real‑time engine
        self.playback_time = 0.0
        self.last_frame_time = time.time()
        self.pixels_per_second = 120.0  # base scroll speed

        # Tempo (BPM)
        self.bpm = 120.0
        self.beats_per_bar = 4  # 4/4 takt

        # Playhead
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
    # REAL‑TIME ENGINE
    # ---------------------------------------------------------
    def _update_time(self):
        now = time.time()
        dt = now - self.last_frame_time
        self.last_frame_time = now
        self.playback_time += dt
        return dt

    # ---------------------------------------------------------
    # POSITIONING
    # ---------------------------------------------------------
    def _pitch_to_y(self, midi: int) -> float:
        return self.margin_top + (60 - midi) * 1.1

    def _time_to_x(self, timestamp: float) -> float:
        return self.playhead_x + (timestamp - self.playback_time) * self.pixels_per_second

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
