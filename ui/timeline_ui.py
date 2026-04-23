import pygame
from typing import Optional

from ..renderer_new.timeline_controller import TimelineController
from ..core.logger import Logger
from ..renderer_new.selection_actions import (
    delete_selected_notes,
    move_selected_notes,
    transpose_selected_notes,
    velocity_selected_notes,
    stretch_selected_notes,
)


class TimelineUI:
    """
    TimelineUI – DAW‑štýlová časová os (FÁZA 4) – VERSION 1.2.0

    Prepojenia:
    - používa TimelineController (renderer_new)
    - synchronizuje markery s GraphicNotationRenderer
    - synchronizuje markery s controller.layout (PixelLayoutEngine)
    - podporuje loop region, playhead seek, drag‑scroll, zoom
    - funguje ako hlavná časová os pre celý projekt

    Tento modul je plne kompatibilný s real‑time pipeline:
        midi_input → notation_engine → renderer_new → TimelineUI
    """

    VERSION = "1.2.0"

    def __init__(self, x, y, width, height, event_bus, renderer):
        pygame.font.init()

        # Pozícia a veľkosť
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.event_bus = event_bus
        self.renderer = renderer  # GraphicNotationRenderer

        # TimelineController (nový timeline systém)
        self.controller = TimelineController(
            width=width,
            height=height,
            bpm=120.0,
            beats_per_bar=4,
            pixels_per_beat=100,
        )

        # Prepojenie s renderer.timeline_controller
        if self.renderer and hasattr(self.renderer, "timeline_controller"):
            if self.renderer.timeline_controller is not None:
                self.controller = self.renderer.timeline_controller
                Logger.info("TimelineUI: prepojené s renderer.timeline_controller")

        # UI zoom/scroll
        self.zoom = 1.0
        self.scroll_x = 0

        # DRAG SCROLL (pravé tlačidlo)
        self.dragging = False
        self.drag_start_x = 0
        self.drag_initial_scroll = 0

        # HANDLE DRAG
        self.handle_dragging = False
        self.handle_drag_offset = 0

        # LOOP REGION
        self.loop_active = False
        self.loop_dragging = False
        self.loop_resizing_left = False
        self.loop_resizing_right = False
        self.loop_start_beat = 0
        self.loop_end_beat = 0
        self.loop_drag_offset = 0

        # MARKERS (DAW PRO)
        # marker: {"beat": float, "label": str, "color": (r,g,b), "type_index": int}
        self.markers = []
        self.marker_dragging: Optional[int] = None
        self.marker_drag_offset = 0
        self.marker_rename_index: Optional[int] = None
        self.marker_rename_text = ""
        self.marker_next_id = 1

        # double‑click tracking
        self._last_click_time = 0
        self._last_click_marker_index: Optional[int] = None
        self._double_click_threshold_ms = 300

        # MARKER COLORS (Ableton palette)
        self.marker_colors = [
            (255, 200, 80),   # yellow
            (255, 150, 50),   # orange
            (255, 80, 80),    # red
            (255, 120, 180),  # pink
            (200, 120, 255),  # purple
            (120, 150, 255),  # blue
            (80, 200, 255),   # cyan
            (80, 255, 180),   # mint
            (120, 255, 120),  # green
            (200, 255, 120),  # lime
            (180, 180, 180),  # gray
            (255, 255, 255),  # white
        ]

        # MARKER TYPES (Unicode ikony + text)
        # SHIFT+T / right‑click cycle type
        self.marker_types = [
            {"name": "Section", "icon": "§"},
            {"name": "Verse", "icon": "♪"},
            {"name": "Chorus", "icon": "★"},
            {"name": "Bridge", "icon": "⇄"},
            {"name": "Cue", "icon": "⚑"},
        ]

        # LAYOUT HEIGHTS
        self.ruler_height = 20
        self.loop_height = 20
        self.marker_lane_height = 24

        # Font
        try:
            self.font = pygame.font.Font(None, 16)
        except Exception:
            self.font = None

        # Playhead vizuál
        self.playhead_color = (255, 80, 80)

        self._recompute_bars()

    # ---------------------------------------------------------
    # PREPOJENIE S PixelLayoutEngine
    # ---------------------------------------------------------
    def set_bounds(self, x, y, w, h):
        self.x = x
        self.y = y
        self.width = w
        self.height = h

        self.controller.set_bounds(w, h)
        self._recompute_bars()

    def _recompute_bars(self):
        self.zoom_bar_rect = pygame.Rect(
            self.x,
            self.y + self.height - 24,
            self.width,
            12,
        )

        self.scroll_bar_rect = pygame.Rect(
            self.x,
            self.y + self.height - 12,
            self.width,
            12,
        )

    # ---------------------------------------------------------
    # HANDLE COMPUTATION
    # ---------------------------------------------------------
    def _compute_handle_rect(self):
        total_width = 200000
        visible_ratio = self.width / (total_width * self.zoom)
        visible_ratio = max(0.02, min(1.0, visible_ratio))

        handle_width = int(self.width * visible_ratio)

        max_scroll = (total_width * self.zoom) - self.width
        if max_scroll <= 0:
            handle_x = self.x
        else:
            scroll_ratio = self.scroll_x / max_scroll
            handle_x = int(self.x + scroll_ratio * (self.width - handle_width))

        return pygame.Rect(handle_x, self.scroll_bar_rect.y, handle_width, self.scroll_bar_rect.h)

    # ---------------------------------------------------------
    # MARKER RECT
    # ---------------------------------------------------------
    def _compute_marker_rect(self, marker):
        layout = self.controller.layout
        px = self.x + layout.beat_to_pixel(marker["beat"]) - self.scroll_x

        lane_y = self.y + self.ruler_height + self.loop_height
        return pygame.Rect(px - 6, lane_y, 12, self.marker_lane_height)

    # ---------------------------------------------------------
    # LOOP RECT
    # ---------------------------------------------------------
    def _compute_loop_rect(self) -> Optional[pygame.Rect]:
        if not self.loop_active:
            return None

        layout = self.controller.layout
        start_px = self.x + layout.beat_to_pixel(self.loop_start_beat) - self.scroll_x
        end_px = self.x + layout.beat_to_pixel(self.loop_end_beat) - self.scroll_x

        if end_px < start_px:
            start_px, end_px = end_px, start_px

        return pygame.Rect(start_px, self.y + self.ruler_height, end_px - start_px, self.loop_height)

    # ---------------------------------------------------------
    # PLAYHEAD RECT
    # ---------------------------------------------------------
    def _compute_playhead_x(self) -> Optional[int]:
        if not hasattr(self.controller, "layout"):
            return None
        layout = self.controller.layout
        beat = getattr(self.controller, "playhead_beat", 0.0)
        px = self.x + layout.beat_to_pixel(beat) - self.scroll_x
        return int(px)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        # 1. Timeline grid
        timeline_surface = self.controller.render()
        if timeline_surface is not None:
            grid_y = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
            surface.blit(timeline_surface, (self.x, grid_y))

        # 2. Ruler
        self._draw_ruler(surface)

        # 3. Loop region
        self._draw_loop(surface)

        # 4. Marker lane
        self._draw_marker_lane(surface)

        # 5. Markers
        self._draw_markers(surface)

        # 6. Playhead
        self._draw_playhead(surface)

        # 7. Bars
        self._draw_zoom_bar(surface)
        self._draw_scroll_bar(surface)

        # 8. Scroll handle
        handle = self._compute_handle_rect()
        pygame.draw.rect(surface, (120, 120, 130), handle, border_radius=3)

    # ---------------------------------------------------------
    # RULER DRAW
    # ---------------------------------------------------------
    def _draw_ruler(self, surface):
        if not self.font:
            return

        layout = self.controller.layout
        beats_per_bar = self.controller.beats_per_bar

        ruler_y = self.y
        ruler_h = self.ruler_height

        pygame.draw.rect(surface, (35, 35, 40), (self.x, ruler_y, self.width, ruler_h))

        start_beat = layout.pixel_to_beat(self.scroll_x)
        end_beat = layout.pixel_to_beat(self.scroll_x + self.width)

        start_beat = int(start_beat) - 2
        end_beat = int(end_beat) + 2

        for beat in range(start_beat, end_beat):
            if beat < 0:
                continue

            px = self.x + layout.beat_to_pixel(beat) - self.scroll_x

            if beat % beats_per_bar == 0:
                pygame.draw.line(surface, (180, 180, 190), (px, ruler_y), (px, ruler_y + ruler_h), 2)
                bar_number = beat // beats_per_bar + 1
                text = self.font.render(str(bar_number), True, (220, 220, 230))
                surface.blit(text, (px + 4, ruler_y + 2))
            else:
                pygame.draw.line(surface, (110, 110, 120), (px, ruler_y + 10), (px, ruler_y + ruler_h), 1)

    # ---------------------------------------------------------
    # LOOP DRAW
    # ---------------------------------------------------------
    def _draw_loop(self, surface):
        rect = self._compute_loop_rect()
        if not rect:
            return

        rect.y = self.y + self.ruler_height
        rect.h = self.loop_height

        # hlavný loop blok
        pygame.draw.rect(surface, (80, 120, 200, 80), rect)
        pygame.draw.rect(surface, (160, 200, 255), rect, 2)

        # vizuálne "handles" na okrajoch (len vizuálne, logika loop už existuje)
        handle_w = 4
        left_handle = pygame.Rect(rect.x - handle_w, rect.y, handle_w, rect.h)
        right_handle = pygame.Rect(rect.right, rect.y, handle_w, rect.h)
        pygame.draw.rect(surface, (200, 230, 255), left_handle)
        pygame.draw.rect(surface, (200, 230, 255), right_handle)

    # ---------------------------------------------------------
    # MARKER LANE DRAW
    # ---------------------------------------------------------
    def _draw_marker_lane(self, surface):
        lane_y = self.y + self.ruler_height + self.loop_height
        pygame.draw.rect(surface, (30, 30, 35), (self.x, lane_y, self.width, self.marker_lane_height))
        # jemná deliaca čiara pod marker lane
        pygame.draw.line(
            surface,
            (50, 50, 60),
            (self.x, lane_y + self.marker_lane_height - 1),
            (self.x + self.width, lane_y + self.marker_lane_height - 1),
            1,
        )

    # ---------------------------------------------------------
    # ZOOM BAR DRAW
    # ---------------------------------------------------------
    def _draw_zoom_bar(self, surface):
        pygame.draw.rect(surface, (25, 25, 30), self.zoom_bar_rect)

        if not self.font:
            return

        # jednoduchý textový indikátor zoomu
        zoom_percent = int(self.zoom * 100)
        text = self.font.render(f"Zoom: {zoom_percent}%", True, (200, 200, 210))
        text_rect = text.get_rect()
        text_rect.centery = self.zoom_bar_rect.centery
        text_rect.x = self.zoom_bar_rect.x + 8
        surface.blit(text, text_rect)

    # ---------------------------------------------------------
    # SCROLL BAR DRAW
    # ---------------------------------------------------------
    def _draw_scroll_bar(self, surface):
        pygame.draw.rect(surface, (20, 20, 25), self.scroll_bar_rect)
        # jemný horný okraj pre oddelenie
        pygame.draw.line(
            surface,
            (45, 45, 55),
            (self.scroll_bar_rect.x, self.scroll_bar_rect.y),
            (self.scroll_bar_rect.x + self.scroll_bar_rect.w, self.scroll_bar_rect.y),
            1,
        )

    # ---------------------------------------------------------
    # PLAYHEAD DRAW
    # ---------------------------------------------------------
    def _draw_playhead(self, surface):
        x = self._compute_playhead_x()
        if x is None:
            return

        grid_top = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
        grid_bottom = self.y + self.height - (self.zoom_bar_rect.h + self.scroll_bar_rect.h)

        pygame.draw.line(surface, self.playhead_color, (x, grid_top), (x, grid_bottom), 2)

    # ---------------------------------------------------------
    # MARKER DRAW
    # ---------------------------------------------------------
    def _draw_markers(self, surface):
        if not self.font:
            return

        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)

            color = marker.get("color", self.marker_colors[0])

            # Triangle marker
            pygame.draw.polygon(
                surface,
                color,
                [
                    (rect.centerx, rect.y),
                    (rect.x, rect.y + rect.h),
                    (rect.right, rect.y + rect.h),
                ],
            )

            # Marker type (Unicode icon)
            type_index = marker.get("type_index", 0) % max(1, len(self.marker_types))
            marker_type = self.marker_types[type_index]
            icon_text = marker_type.get("icon", "")

            text_x = rect.centerx + 4
            if icon_text:
                icon_surf = self.font.render(icon_text, True, color)
                surface.blit(icon_surf, (text_x, rect.y + 2))
                text_x += icon_surf.get_width() + 4

            # Label or rename box
            if self.marker_rename_index == i:
                text = self.font.render(self.marker_rename_text, True, (0, 0, 0))
                box_w = max(40, text.get_width() + 10)
                box_h = text.get_height() + 6
                box_rect = pygame.Rect(text_x, rect.y + 2, box_w, box_h)
                pygame.draw.rect(surface, (255, 255, 255), box_rect)
                pygame.draw.rect(surface, (0, 0, 0), box_rect, 1)
                surface.blit(text, (box_rect.x + 4, box_rect.y + 3))
            else:
                text = self.font.render(marker["label"], True, color)
                surface.blit(text, (text_x, rect.y + 2))
