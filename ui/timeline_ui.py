import pygame
from typing import Optional
from ..renderer_new.timeline_controller import TimelineController
from ..core.logger import Logger


class TimelineUI:
    """
    Timeline UI – DAW‑štýlová časová os.
    Prepojené s TimelineController (renderer_new).
    """

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
            pixels_per_beat=100
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
        self.markers = []  # {"beat": float, "label": "M1", "color": (r,g,b)}
        self.marker_dragging = None
        self.marker_drag_offset = 0
        self.marker_rename_index = None
        self.marker_rename_text = ""
        self.marker_next_id = 1

        # double‑click tracking
        self._last_click_time = 0
        self._last_click_marker_index = None
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

        # LAYOUT HEIGHTS
        self.ruler_height = 20
        self.loop_height = 20
        self.marker_lane_height = 24

        # Font
        try:
            self.font = pygame.font.Font(None, 16)
        except Exception:
            self.font = None

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

        # 6. Bars
        self._draw_zoom_bar(surface)
        self._draw_scroll_bar(surface)

        # 7. Scroll handle
        handle = self._compute_handle_rect()
        pygame.draw.rect(surface, (120, 120, 130), handle)

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

        pygame.draw.rect(surface, (80, 120, 200, 80), rect)
        pygame.draw.rect(surface, (160, 200, 255), rect, 2)

    # ---------------------------------------------------------
    # MARKER LANE DRAW
    # ---------------------------------------------------------
    def _draw_marker_lane(self, surface):
        lane_y = self.y + self.ruler_height + self.loop_height
        pygame.draw.rect(surface, (30, 30, 35), (self.x, lane_y, self.width, self.marker_lane_height))

    # ---------------------------------------------------------
    # MARKER DRAW
    # ---------------------------------------------------------
    def _draw_markers(self, surface):
        if not self.font:
            return

        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)

            color = marker.get("color", (255, 200, 80))

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

            # Label or rename box
            if self.marker_rename_index == i:
                text = self.font.render(self.marker_rename_text, True, (0, 0, 0))
                box_w = max(40, text.get_width() + 10)
                box_h = text.get_height() + 6
                box_rect = pygame.Rect(rect.centerx + 4, rect.y + 2, box_w, box_h)
                pygame.draw.rect(surface, (255, 255, 255), box_rect)
                pygame.draw.rect(surface, (0, 0, 0), box_rect, 1)
                surface.blit(text, (box_rect.x + 4, box_rect.y + 3))
            else:
                text = self.font.render(marker["label"], True, color)
                surface.blit(text, (rect.centerx + 4, rect.y + 2))

    # ---------------------------------------------------------
    # SNAPPING HELPERS
    # ---------------------------------------------------------
    def _snap_beat(self, beat):
        mods = pygame.key.get_mods()
        beats_per_bar = self.controller.beats_per_bar

        # SHIFT = disable snapping
        if mods & pygame.KMOD_SHIFT:
            return beat

        # CTRL = snap to bars
        if mods & pygame.KMOD_CTRL:
            return round(beat / beats_per_bar) * beats_per_bar

        # default = snap to nearest beat
        return round(beat)

    # ---------------------------------------------------------
    # MARKER COLOR LOGIC
    # ---------------------------------------------------------
    def _cycle_marker_color(self, index):
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
    # MARKER LOGIC
    # ---------------------------------------------------------
    def _add_marker(self, mouse_x):
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        beat = self._snap_beat(beat)

        label = f"M{self.marker_next_id}"
        self.marker_next_id += 1

        self.markers.append({
            "beat": beat,
            "label": label,
            "color": self.marker_colors[0]
        })
        self._sync_markers()

    def _delete_marker(self, index):
        del self.markers[index]
        self._sync_markers()

    def _start_marker_drag(self, index, mouse_x):
        self.marker_dragging = index
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)
        self.marker_drag_offset = beat - self.markers[index]["beat"]

    def _update_marker_drag(self, mouse_x):
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

    def _end_marker_drag(self):
        self.marker_dragging = None

    def _start_marker_rename(self, index):
        self.marker_rename_index = index
        self.marker_rename_text = self.markers[index]["label"]

    def _commit_marker_rename(self):
        if self.marker_rename_index is not None:
            self.markers[self.marker_rename_index]["label"] = self.marker_rename_text
            self._sync_markers()
        self.marker_rename_index = None
        self.marker_rename_text = ""

    def _cancel_marker_rename(self):
        self.marker_rename_index = None
        self.marker_rename_text = ""

    def _sync_markers(self):
        if hasattr(self.renderer, "set_markers"):
            try:
                self.renderer.set_markers(self.markers)
            except:
                pass

        if hasattr(self.controller.layout, "set_markers"):
            try:
                self.controller.layout.set_markers(self.markers)
            except:
                pass

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()

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

        # MARKER INTERACTION
        for i, marker in enumerate(self.markers):
            rect = self._compute_marker_rect(marker)

            # RIGHT CLICK → delete
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                if rect.collidepoint(mx, my):
                    self._delete_marker(i)
                    return None

            # SHIFT + C → cycle color
            if event.type == pygame.KEYDOWN and event.key == pygame.K_c:
                mods = pygame.key.get_mods()
                if mods & pygame.KMOD_SHIFT:
                    if rect.collidepoint(mx, my):
                        self._cycle_marker_color(i)
                        return None

            # LEFT CLICK: drag or rename (double‑click)
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
        grid_y = self.y + self.ruler_height + self.loop
