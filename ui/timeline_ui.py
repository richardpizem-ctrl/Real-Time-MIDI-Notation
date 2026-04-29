import math
import pygame
from typing import Optional, List, Dict, Any

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
    TimelineUI – DAW‑štýlová časová os (FÁZA 4) – VERSION 1.3.0

    Prepojenia:
    - používa TimelineController (renderer_new)
    - synchronizuje markery s GraphicNotationRenderer
    - synchronizuje markery s controller.layout (PixelLayoutEngine)
    - podporuje loop region, playhead seek, drag‑scroll, zoom
    - funguje ako hlavná časová os pre celý projekt

    Tento modul je plne kompatibilný s real‑time pipeline:
        midi_input → notation_engine → renderer_new → TimelineUI
    """

    VERSION = "1.3.0"

    def __init__(self, x: int, y: int, width: int, height: int, event_bus, renderer):
        pygame.font.init()

        # Pozícia a veľkosť
        self.x: int = x
        self.y: int = y
        self.width: int = width
        self.height: int = height

        self.event_bus = event_bus
        self.renderer = renderer  # GraphicNotationRenderer

        # TimelineController (nový timeline systém)
        self.controller: TimelineController = TimelineController(
            width=width,
            height=height,
            bpm=120.0,
            beats_per_bar=4,
            pixels_per_beat=100,
        )

        # Prepojenie s renderer.timeline_controller (ak existuje)
        if self.renderer and hasattr(self.renderer, "timeline_controller"):
            if self.renderer.timeline_controller is not None:
                self.controller = self.renderer.timeline_controller
                Logger.info("TimelineUI: prepojené s renderer.timeline_controller")

        # UI zoom/scroll
        self.zoom: float = 1.0
        self.scroll_x: int = 0

        # DRAG SCROLL (pravé tlačidlo)
        self.dragging: bool = False
        self.drag_start_x: int = 0
        self.drag_initial_scroll: int = 0

        # HANDLE DRAG
        self.handle_dragging: bool = False
        self.handle_drag_offset: int = 0

        # LOOP REGION
        self.loop_active: bool = False
        self.loop_dragging: bool = False
        self.loop_resizing_left: bool = False
        self.loop_resizing_right: bool = False
        self.loop_start_beat: float = 0.0
        self.loop_end_beat: float = 0.0
        self.loop_drag_offset: float = 0.0

        # LOOP HOVER
        self.loop_hover: bool = False

        # MARKERS (DAW PRO)
        # marker: {"beat": float, "label": str, "color": (r,g,b), "type_index": int}
        self.markers: List[Dict[str, Any]] = []
        self.marker_dragging: Optional[int] = None
        self.marker_drag_offset: float = 0.0
        self.marker_rename_index: Optional[int] = None
        self.marker_rename_text: str = ""
        self.marker_next_id: int = 1

        # HOVER – index markeru pod myšou
        self.hover_marker_index: Optional[int] = None

        # PLAYHEAD HOVER
        self.playhead_hover: bool = False

        # GHOST LINES (snapping vizuál)
        self.ghost_x: Optional[int] = None

        # TRACK SWITCHER UI (príprava na 1.4.0)
        self.tracks: List[Dict[str, Any]] = [
            {"name": "Track 1", "color": (120, 180, 255)},
            {"name": "Track 2", "color": (180, 120, 255)},
            {"name": "Track 3", "color": (120, 255, 180)},
        ]
        self.active_track_index: int = 0
        self.track_button_rects: List[pygame.Rect] = []
        self.track_switcher_height: int = 18

        # double‑click tracking
        self._last_click_time: int = 0
        self._last_click_marker_index: Optional[int] = None
        self._double_click_threshold_ms: int = 300

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
        self.ruler_height: int = 20
        self.loop_height: int = 20
        self.marker_lane_height: int = 24

        # Font
        try:
            self.font = pygame.font.Font(None, 16)
        except Exception:
            self.font = None

        # Playhead vizuál
        self.playhead_color = (255, 80, 80)

        # Interné recty pre zoom/scroll bary
        self.zoom_bar_rect: pygame.Rect
        self.scroll_bar_rect: pygame.Rect
        self._recompute_bars()

    # ---------------------------------------------------------
    # PREPOJENIE S PixelLayoutEngine
    # ---------------------------------------------------------
    def set_bounds(self, x: int, y: int, w: int, h: int) -> None:
        self.x = x
        self.y = y
        self.width = w
        self.height = h

        self.controller.set_bounds(w, h)
        self._recompute_bars()

    def _recompute_bars(self) -> None:
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
    def _compute_handle_rect(self) -> pygame.Rect:
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
    def _compute_marker_rect(self, marker: Dict[str, Any]) -> pygame.Rect:
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
    # PLAYHEAD X
    # ---------------------------------------------------------
    def _compute_playhead_x(self) -> Optional[int]:
        if not hasattr(self.controller, "layout"):
            return None
        layout = self.controller.layout
        beat = getattr(self.controller, "playhead_beat", 0.0)
        px = self.x + layout.beat_to_pixel(beat) - self.scroll_x
        return int(px)

    # ---------------------------------------------------------
    # HOVER PULSE (jemné animácie)
    # ---------------------------------------------------------
    def _get_hover_pulse(self) -> int:
        t = pygame.time.get_ticks()
        phase = (t % 1000) / 1000.0 * 2 * math.pi
        # 0 – 40
        return int(20 + 20 * (math.sin(phase) * 0.5 + 0.5))

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface) -> None:
        # 0. Track Switcher UI (nad rulerom)
        self._draw_track_switcher(surface)

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

        # 6. Ghost snapping line
        self._draw_ghost_line(surface)

        # 7. Playhead
        self._draw_playhead(surface)

        # 8. Bars
        self._draw_zoom_bar(surface)
        self._draw_scroll_bar(surface)

        # 9. Scroll handle
        handle = self._compute_handle_rect()
        pygame.draw.rect(surface, (120, 120, 130), handle, border_radius=3)

    # ---------------------------------------------------------
    # TRACK SWITCHER DRAW
    # ---------------------------------------------------------
    def _draw_track_switcher(self, surface: pygame.Surface) -> None:
        if not self.tracks or not self.font:
            return

        bar_y = self.y - self.track_switcher_height
        bar_h = self.track_switcher_height
        bar_rect = pygame.Rect(self.x, bar_y, self.width, bar_h)

        pygame.draw.rect(surface, (20, 20, 25), bar_rect)
        pygame.draw.line(surface, (60, 60, 70), (bar_rect.x, bar_rect.bottom - 1), (bar_rect.right, bar_rect.bottom - 1), 1)

        self.track_button_rects = []
        padding = 6
        btn_x = self.x + padding
        btn_h = bar_h - 6

        for idx, track in enumerate(self.tracks):
            name = track.get("name", f"T{idx+1}")
            color = track.get("color", (120, 150, 255))
            text_surf = self.font.render(name, True, (230, 230, 235))
            btn_w = text_surf.get_width() + 16
            btn_rect = pygame.Rect(btn_x, bar_y + 3, btn_w, btn_h)

            is_active = (idx == self.active_track_index)
            base_color = color
            if is_active:
                pulse = self._get_hover_pulse()
                base_color = (
                    min(255, color[0] + pulse // 2),
                    min(255, color[1] + pulse // 2),
                    min(255, color[2] + pulse // 2),
                )

            pygame.draw.rect(surface, base_color, btn_rect, border_radius=4)
            pygame.draw.rect(surface, (10, 10, 15), btn_rect, 1, border_radius=4)
            surface.blit(text_surf, (btn_rect.x + 8, btn_rect.y + (btn_rect.h - text_surf.get_height()) // 2))

            self.track_button_rects.append(btn_rect)
            btn_x += btn_w + padding

    # ---------------------------------------------------------
    # RULER DRAW
    # ---------------------------------------------------------
    def _draw_ruler(self, surface: pygame.Surface) -> None:
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
    # LOOP DRAW (s hover efektom)
    # ---------------------------------------------------------
    def _draw_loop(self, surface: pygame.Surface) -> None:
        rect = self._compute_loop_rect()
        if not rect:
            return

        rect.y = self.y + self.ruler_height
        rect.h = self.loop_height

        base_fill = (80, 120, 200, 80)
        base_border = (160, 200, 255)

        if self.loop_hover:
            pulse = self._get_hover_pulse()
            base_border = (
                min(255, base_border[0] + pulse),
                min(255, base_border[1] + pulse),
                min(255, base_border[2] + pulse),
            )

        pygame.draw.rect(surface, base_fill, rect)
        pygame.draw.rect(surface, base_border, rect, 2)

        handle_w = 4
        left_handle = pygame.Rect(rect.x - handle_w, rect.y, handle_w, rect.h)
        right_handle = pygame.Rect(rect.right, rect.y, handle_w, rect.h)
        pygame.draw.rect(surface, (200, 230, 255), left_handle)
        pygame.draw.rect(surface, (200, 230, 255), right_handle)

    # ---------------------------------------------------------
    # MARKER LANE DRAW
    # ---------------------------------------------------------
    def _draw_marker_lane(self, surface: pygame.Surface) -> None:
        lane_y = self.y + self.ruler_height + self.loop_height
        pygame.draw.rect(surface, (30, 30, 35), (self.x, lane_y, self.width, self.marker_lane_height))
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
    def _draw_zoom_bar(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (25, 25, 30), self.zoom_bar_rect)

        if not self.font:
            return

        zoom_percent = int(self.zoom * 100)
        text = self.font.render(f"Zoom: {zoom_percent}%", True, (200, 200, 210))
        text_rect = text.get_rect()
        text_rect.centery = self.zoom_bar_rect.centery
        text_rect.x = self.zoom_bar_rect.x + 8
        surface.blit(text, text_rect)

    # ---------------------------------------------------------
    # SCROLL BAR DRAW
    # ---------------------------------------------------------
    def _draw_scroll_bar(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (20, 20, 25), self.scroll_bar_rect)
        pygame.draw.line(
            surface,
            (45, 45, 55),
            (self.scroll_bar_rect.x, self.scroll_bar_rect.y),
            (self.scroll_bar_rect.x + self.scroll_bar_rect.w, self.scroll_bar_rect.y),
            1,
        )

    # ---------------------------------------------------------
    # GHOST LINE DRAW (snapping vizuál)
    # ---------------------------------------------------------
    def _draw_ghost_line(self, surface: pygame.Surface) -> None:
        if self.ghost_x is None:
            return

        grid_top = self.y + self.ruler_height
        grid_bottom = self.y + self.height - (self.zoom_bar_rect.h + self.scroll_bar_rect.h)

        pulse = self._get_hover_pulse()
        color = (100 + pulse // 2, 100 + pulse // 2, 160 + pulse // 2)

        pygame.draw.line(surface, color, (self.ghost_x, grid_top), (self.ghost_x, grid_bottom), 1)

    # ---------------------------------------------------------
    # PLAYHEAD DRAW (s hover efektom)
    # ---------------------------------------------------------
    def _draw_playhead(self, surface: pygame.Surface) -> None:
        x = self._compute_playhead_x()
        if x is None:
            return

        grid_top = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
        grid_bottom = self.y + self.height - (self.zoom_bar_rect.h + self.scroll_bar_rect.h)

        color = self.playhead_color
        width = 2
        if self.playhead_hover:
            pulse = self._get_hover_pulse()
            color = (
                min(255, color[0] + pulse),
                min(255, color[1] + pulse // 2),
                min(255, color[2] + pulse // 2),
            )
            width = 3

        pygame.draw.line(surface, color, (x, grid_top), (x, grid_bottom), width)

    # ---------------------------------------------------------
    # MARKER DRAW (s hover efektom)
    # ---------------------------------------------------------
    def _draw_markers(self, surface: pygame.Surface) -> None:
        if not self.font:
            return

        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)

            color = marker.get("color", self.marker_colors[0])

            is_hover = (self.hover_marker_index == i)
            if is_hover:
                pulse = self._get_hover_pulse()
                hover_rect = rect.inflate(6, 4)
                pygame.draw.rect(surface, (255, 255, 255, 40), hover_rect, border_radius=3)
                border_color = (200 + pulse // 2, 200 + pulse // 2, 200 + pulse // 2)
                pygame.draw.rect(surface, border_color, hover_rect, 1)

            pygame.draw.polygon(
                surface,
                color,
                [
                    (rect.centerx, rect.y),
                    (rect.x, rect.y + rect.h),
                    (rect.right, rect.y + rect.h),
                ],
            )

            type_index = marker.get("type_index", 0) % max(1, len(self.marker_types))
            marker_type = self.marker_types[type_index]
            icon_text = marker_type.get("icon", "")

            text_x = rect.centerx + 4
            if icon_text:
                icon_surf = self.font.render(icon_text, True, color)
                surface.blit(icon_surf, (text_x, rect.y + 2))
                text_x += icon_surf.get_width() + 4

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

    # ---------------------------------------------------------
    # SNAPPING HELPERS
    # ---------------------------------------------------------
    def _snap_beat(self, beat: float) -> float:
        mods = pygame.key.get_mods()
        beats_per_bar = self.controller.beats_per_bar

        if mods & pygame.KMOD_SHIFT:
            return beat

        if mods & pygame.KMOD_CTRL:
            return round(beat / beats_per_bar) * beats_per_bar

        return round(beat)

    # ---------------------------------------------------------
    # MARKER COLOR LOGIC
    # ---------------------------------------------------------
    def _cycle_marker_color(self, index: int) -> None:
        marker = self.markers[index]
        current = marker.get("color", self.marker_colors[0])

        if current not in self.marker_colors:
            new_color = self.marker_colors[0]
        else:
            idx = self.marker_colors.index(current)
            new_color = self.marker_colors[(idx + 1) % len(self.marker_colors)]

        marker["color"] = new_color
        self._sync_markers()

    # ---------------------------------------------------------
    # MARKER TYPE LOGIC
    # ---------------------------------------------------------
    def _cycle_marker_type(self, index: int) -> None:
        if not self.marker_types:
            return
        marker = self.markers[index]
        current = marker.get("type_index", 0)
        new_index = (current + 1) % len(self.marker_types)
        marker["type_index"] = new_index
        self._sync_markers()

    # ---------------------------------------------------------
    # MARKER LOGIC
    # ---------------------------------------------------------
    def _add_marker(self, mouse_x: int) -> None:
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        beat = self._snap_beat(beat)

        label = f"M{self.marker_next_id}"
        self.marker_next_id += 1

        self.markers.append(
            {
                "beat": beat,
                "label": label,
                "color": self.marker_colors[0],
                "type_index": 0,
            }
        )
        self._sync_markers()

    def _delete_marker(self, index: int) -> None:
        del self.markers[index]
        self._sync_markers()

    def _start_marker_drag(self, index: int, mouse_x: int) -> None:
        self.marker_dragging = index
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)
        self.marker_drag_offset = beat - self.markers[index]["beat"]

    def _update_marker_drag(self, mouse_x: int) -> None:
        if self.marker_dragging is None:
            return

        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        new_beat = beat - self.marker_drag_offset
        new_beat = self._snap_beat(new_beat)

        if new_beat < 0:
            new_beat = 0

        self.markers[self.marker_dragging]["beat"] = new_beat
        self._sync_markers()

    def _end_marker_drag(self) -> None:
        self.marker_dragging = None

    def _start_marker_rename(self, index: int) -> None:
        self.marker_rename_index = index
        self.marker_rename_text = self.markers[index]["label"]

    def _commit_marker_rename(self) -> None:
        if self.marker_rename_index is not None:
            self.markers[self.marker_rename_index]["label"] = self.marker_rename_text
            self._sync_markers()
        self.marker_rename_index = None
        self.marker_rename_text = ""

    def _cancel_marker_rename(self) -> None:
        self.marker_rename_index = None
        self.marker_rename_text = ""

    def _sync_markers(self) -> None:
        if hasattr(self.renderer, "set_markers"):
            try:
                self.renderer.set_markers(self.markers)
            except Exception:
                pass

        if hasattr(self.controller.layout, "set_markers"):
            try:
                self.controller.layout.set_markers(self.markers)
            except Exception:
                pass

    # ---------------------------------------------------------
    # LOOP LOGIC
    # ---------------------------------------------------------
    def _start_loop(self, mouse_x: int) -> None:
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)
        beat = self._snap_beat(beat)

        self.loop_active = True
        self.loop_start_beat = beat
        self.loop_end_beat = beat

    def _update_loop(self, mouse_x: int) -> None:
        if not self.loop_active:
            return
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)
        beat = self._snap_beat(beat)
        self.loop_end_beat = max(0.0, beat)

    def _finalize_loop(self) -> None:
        if not self.loop_active:
            return

        if self.loop_end_beat < self.loop_start_beat:
            self.loop_start_beat, self.loop_end_beat = self.loop_end_beat, self.loop_start_beat

        if hasattr(self.controller, "set_loop_region"):
            try:
                self.controller.set_loop_region(self.loop_start_beat, self.loop_end_beat)
            except Exception:
                pass

    # ---------------------------------------------------------
    # HANDLE DRAG LOGIC
    # ---------------------------------------------------------
    def _start_handle_drag(self, mouse_x: int) -> None:
        self.handle_dragging = True
        handle = self._compute_handle_rect()
        self.handle_drag_offset = mouse_x - handle.x

    def _update_handle_drag(self, mouse_x: int) -> None:
        handle = self._compute_handle_rect()
        new_x = mouse_x - self.handle_drag_offset

        new_x = max(self.x, min(self.x + self.width - handle.w, new_x))

        total_width = 200000
        max_scroll = (total_width * self.zoom) - self.width
        if max_scroll <= 0:
            self.scroll_x = 0
            return

        scroll_ratio = (new_x - self.x) / (self.width - handle.w)
        self.scroll_x = int(scroll_ratio * max_scroll)

    def _end_handle_drag(self) -> None:
        self.handle_dragging = False
        self.handle_drag_offset = 0

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event) -> Optional[None]:
        mx, my = pygame.mouse.get_pos()

        # HOVER DETECTION FOR MARKERS
        self.hover_marker_index = None
        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)
            if rect.collidepoint(mx, my):
                self.hover_marker_index = i
                break

        # HOVER DETECTION FOR LOOP
        loop_rect = self._compute_loop_rect()
        self.loop_hover = bool(loop_rect and loop_rect.collidepoint(mx, my))

        # HOVER DETECTION FOR PLAYHEAD
        self.playhead_hover = False
        x_playhead = self._compute_playhead_x()
        if x_playhead is not None:
            grid_top = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
            grid_bottom = self.y + self.height - (self.zoom_bar_rect.h + self.scroll_bar_rect.h)
            if abs(mx - x_playhead) <= 3 and grid_top <= my <= grid_bottom:
                self.playhead_hover = True

        # GHOST LINE UPDATE (snapping vizuál)
        self.ghost_x = None
        if hasattr(self.controller, "layout"):
            layout = self.controller.layout
            # ruler alebo grid
            in_ruler = self.y <= my <= self.y + self.ruler_height
            grid_y = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
            grid_h = self.height - (
                self.ruler_height
                + self.loop_height
                + self.marker_lane_height
                + self.zoom_bar_rect.h
                + self.scroll_bar_rect.h
            )
            if grid_h < 0:
                grid_h = 0
            in_grid = grid_y <= my <= grid_y + grid_h

            if in_ruler or in_grid:
                beat = layout.pixel_to_beat(mx - self.x + self.scroll_x)
                beat = self._snap_beat(beat)
                px = self.x + layout.beat_to_pixel(beat) - self.scroll_x
                self.ghost_x = int(px)

        # TEXT INPUT FOR MARKER RENAME
        if self.marker_rename_index is not None and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self._commit_marker_rename()
                return None
            if event.key == pygame.K_ESCAPE:
                self._cancel_marker_rename()
                return None
            if event.key == pygame.K_BACKSPACE:
                self.marker_rename_text = self.marker_rename_text[:-1]
                return None
            if event.unicode and event.key != pygame.K_TAB:
                self.marker_rename_text += event.unicode
                return None

        # TRACK SWITCHER CLICK
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for idx, rect in enumerate(self.track_button_rects):
                if rect.collidepoint(mx, my):
                    if idx != self.active_track_index:
                        self.active_track_index = idx
                        if self.event_bus and hasattr(self.event_bus, "publish"):
                            try:
                                self.event_bus.publish("timeline.track_switched", index=idx)
                            except Exception:
                                pass
                    return None

        # MARKER INTERACTION
        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if rect.collidepoint(mx, my):
                    mods = pygame.key.get_mods()
                    if mods & pygame.KMOD_CTRL:
                        self._delete_marker(i)
                    else:
                        self._cycle_marker_type(i)
                    return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    if rect.collidepoint(mx, my):
                        self._cycle_marker_color(i)
                        return None

            if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    if rect.collidepoint(mx, my):
                        self._cycle_marker_type(i)
                        return None

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect.collidepoint(mx, my):
                    now = pygame.time.get_ticks()
                    if (
                        self._last_click_marker_index == i
                        and now - self._last_click_time <= self._double_click_threshold_ms
                    ):
                        self._start_marker_rename(i)
                    else:
                        self._start_marker_drag(i, mx)
                    self._last_click_time = now
                    self._last_click_marker_index = i
                    return None

        # MARKER DRAG MOVE
        if event.type == pygame.MOUSEMOTION:
            if self.marker_dragging is not None:
                self._update_marker_drag(mx)
                return None

        # MARKER DRAG END
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.marker_dragging is not None:
                self._end_marker_drag()
                return None

        # ADD MARKER (SHIFT + LEFT CLICK in marker lane)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mods = pygame.key.get_mods()
            lane_y = self.y + self.ruler_height + self.loop_height
            if mods & pygame.KMOD_SHIFT:
                if lane_y <= my <= lane_y + self.marker_lane_height:
                    self._add_marker(mx)
                    return None

        # LOOP REGION START (left click in ruler)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.y <= my <= self.y + self.ruler_height:
                self._start_loop(mx)
                return None

        # LOOP REGION UPDATE
        if event.type == pygame.MOUSEMOTION:
            if self.loop_active and not self.handle_dragging and not self.dragging:
                if pygame.mouse.get_pressed()[0]:
                    self._update_loop(mx)
                    return None

        # LOOP REGION FINALIZE
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.loop_active:
                self._finalize_loop()
                return None

        # HANDLE DRAG START
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            handle = self._compute_handle_rect()
            if handle.collidepoint(mx, my):
                self._start_handle_drag(mx)
                return None

        # HANDLE DRAG MOVE
        if event.type == pygame.MOUSEMOTION:
            if self.handle_dragging:
                self._update_handle_drag(mx)
                return None

        # HANDLE DRAG END
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self._end_handle_drag()

        # CLICK‑TO‑SEEK (grid area)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            grid_y = self.y + self.ruler_height + self.loop_height + self.marker_lane_height
            grid_h = self.height - (
                self.ruler_height
                + self.loop_height
                + self.marker_lane_height
                + self.zoom_bar_rect.h
                + self.scroll_bar_rect.h
            )
            if grid_h < 0:
                grid_h = 0
            if grid_y <= my <= grid_y + grid_h:
                layout = self.controller.layout
                beat = layout.pixel_to_beat(mx - self.x + self.scroll_x)
                beat = max(0.0, beat)
                if hasattr(self.controller, "set_playhead_beat"):
                    try:
                        self.controller.set_playhead_beat(beat)
                    except Exception:
                        pass
                elif hasattr(self.controller, "playhead_beat"):
                    self.controller.playhead_beat = beat
                return None

        # ---------------------------------------------------------
        # SELECTION KEYBOARD ACTIONS
        # ---------------------------------------------------------
        if event.type == pygame.KEYDOWN and hasattr(self.renderer, "notes"):
            notes = self.renderer.notes
            selected_indices: List[int] = []

            if hasattr(self.renderer, "get_selected_indices"):
                try:
                    selected_indices = self.renderer.get_selected_indices()
                except Exception:
                    selected_indices = []

            if event.key == pygame.K_DELETE:
                self.renderer.notes = delete_selected_notes(notes, selected_indices)
                return None

            if event.key == pygame.K_LEFT:
                self.renderer.notes = move_selected_notes(notes, selected_indices, dx=-10, dy=0)
                return None

            if event.key == pygame.K_RIGHT:
                self.renderer.notes = move_selected_notes(notes, selected_indices, dx=10, dy=0)
                return None

            if event.key == pygame.K_UP:
                self.renderer.notes = transpose_selected_notes(notes, selected_indices, semitones=1)
                return None

            if event.key == pygame.K_DOWN:
                self.renderer.notes = transpose_selected_notes(notes, selected_indices, semitones=-1)
                return None

            if event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                self.renderer.notes = velocity_selected_notes(notes, selected_indices, delta=5)
                return None

            if event.key == pygame.K_MINUS:
                self.renderer.notes = velocity_selected_notes(notes, selected_indices, delta=-5)
                return None

            mods = pygame.key.get_mods()
            if event.key == pygame.K_COMMA and (mods & pygame.KMOD_SHIFT):
                self.renderer.notes = stretch_selected_notes(notes, selected_indices, factor=0.9)
                return None
            if event.key == pygame.K_PERIOD and (mods & pygame.KMOD_SHIFT):
                self.renderer.notes = stretch_selected_notes(notes, selected_indices, factor=1.1)
                return None

        return None
