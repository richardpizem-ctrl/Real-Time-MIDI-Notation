import pygame
import math


class TimelineUI:
    """
    Timeline UI – DAW‑štýlová časová os.
    """

    def __init__(self, x, y, width, height, event_bus, renderer):
        pygame.font.init()

        # Dynamické rozmery – budú aktualizované PixelLayoutEngine-om
        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.event_bus = event_bus
        self.renderer = renderer

        # Zoom & scroll
        self.zoom = 1.0
        self.min_zoom = 0.25
        self.max_zoom = 4.0
        self.scroll_x = 0

        # Grid
        self.beats_per_bar = 4
        self.pixels_per_beat = 40

        # Playback head
        self.playhead_x = 0

        # Loop region
        self.loop_start = None
        self.loop_end = None
        self.loop_dragging = False
        self.loop_resizing_left = False
        self.loop_resizing_right = False
        self.loop_drag_offset = 0

        # Marker lane
        self.marker_lane_height = 25
        self.markers = []
        self.selected_marker = None
        self.marker_dragging = False
        self.marker_drag_offset = 0

        # Selection region
        self.sel_start = None
        self.sel_end = None
        self.sel_dragging = False
        self.sel_resizing_left = False
        self.sel_resizing_right = False
        self.sel_drag_offset = 0

        # Zoom bar
        self.zoom_bar_height = 12
        self.zoom_thumb_width = 40
        self.zoom_thumb_dragging = False

        # Scroll bar
        self.scroll_bar_height = 12
        self.scroll_thumb_dragging = False
        self.scroll_thumb_offset = 0

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
        """PixelLayoutEngine nastaví rozmery timeline."""
        self.x = x
        self.y = y
        self.width = w
        self.height = h
        self._recompute_bars()

    def _recompute_bars(self):
        """Prepočíta pozície zoom a scroll barov podľa aktuálnej veľkosti."""
        self.zoom_bar_rect = pygame.Rect(
            self.x,
            self.y + self.height - self.zoom_bar_height - self.scroll_bar_height - 2,
            self.width,
            self.zoom_bar_height
        )

        self.scroll_bar_rect = pygame.Rect(
            self.x,
            self.y + self.height - self.scroll_bar_height,
            self.width,
            self.scroll_bar_height
        )

    # ---------------------------------------------------------
    # GRID VÝPOČTY
    # ---------------------------------------------------------
    def _beat_to_x(self, beat_index):
        return int(self.x + (beat_index * self.pixels_per_beat * self.zoom) - self.scroll_x)

    def _x_to_beat(self, x):
        return (x + self.scroll_x - self.x) / (self.pixels_per_beat * self.zoom)

    def _bar_to_x(self, bar_index):
        return self._beat_to_x(bar_index * self.beats_per_bar)

    # ---------------------------------------------------------
    # DRAW HELPERS – DAW VIZUÁLNY POLISH
    # ---------------------------------------------------------
    def _draw_background(self, surface):
        top_color = (40, 40, 45)
        bottom_color = (20, 20, 22)
        h = self.height

        for i in range(h):
            t = i / max(1, h - 1)
            r = int(top_color[0] * (1 - t) + bottom_color[0] * t)
            g = int(top_color[1] * (1 - t) + bottom_color[1] * t)
            b = int(top_color[2] * (1 - t) + bottom_color[2] * t)
            pygame.draw.line(surface, (r, g, b),
                             (self.x, self.y + i),
                             (self.x + self.width, self.y + i))

        pygame.draw.rect(surface, (70, 70, 75),
                         (self.x, self.y, self.width, self.height), 1)

        sep_y = self.y + self.height - self.scroll_bar_height - 1
        pygame.draw.line(surface, (15, 15, 15),
                         (self.x, sep_y),
                         (self.x + self.width, sep_y))

    def _draw_marker_lane(self, surface):
        lane_rect = pygame.Rect(self.x, self.y, self.width, self.marker_lane_height)

        left_color = (55, 55, 60)
        right_color = (35, 35, 40)
        for i in range(self.width):
            t = i / max(1, self.width - 1)
            r = int(left_color[0] * (1 - t) + right_color[0] * t)
            g = int(left_color[1] * (1 - t) + right_color[1] * t)
            b = int(left_color[2] * (1 - t) + right_color[2] * t)
            surface.set_at((self.x + i, self.y), (r, g, b))

        pygame.draw.rect(surface, (45, 45, 50), lane_rect)

        pygame.draw.line(surface, (80, 80, 90),
                         (self.x, self.y + self.marker_lane_height - 1),
                         (self.x + self.width, self.y + self.marker_lane_height - 1))

        for i, marker in enumerate(self.markers):
            x = self._beat_to_x(marker["beat"])
            if x < self.x - 20 or x > self.x + self.width + 20:
                continue

            base_color = (255, 190, 60) if i == self.selected_marker else (240, 170, 40)
            body_rect = pygame.Rect(x - 5, self.y + 5, 10, 15)

            glow_surf = pygame.Surface((body_rect.width + 8, body_rect.height + 8), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (base_color[0], base_color[1], base_color[2], 80),
                             glow_surf.get_rect(), border_radius=6)
            surface.blit(glow_surf, (body_rect.x - 4, body_rect.y - 4))

            pygame.draw.rect(surface, base_color, body_rect, border_radius=3)

            if self.font:
                txt = self.font.render(marker["label"], True, (0, 0, 0))
                surface.blit(txt, (x - txt.get_width() // 2, self.y + 6))

    def _draw_bars(self, surface):
        total_bars = 200
        for bar in range(total_bars):
            x = self._bar_to_x(bar)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            pygame.draw.line(surface, (210, 210, 215),
                             (x, self.y + self.marker_lane_height),
                             (x, self.y + self.height - 24), 2)

            pygame.draw.line(surface, (80, 80, 85),
                             (x + 1, self.y + self.marker_lane_height),
                             (x + 1, self.y + self.height - 24), 1)

            if self.font:
                txt = self.font.render(str(bar + 1), True, (230, 230, 235))
                surface.blit(txt, (x + 4, self.y + self.marker_lane_height + 4))

    def _draw_beats(self, surface):
        total_beats = 800
        for beat in range(total_beats):
            x = self._beat_to_x(beat)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            color = (120, 120, 125) if beat % self.beats_per_bar == 0 else (70, 70, 75)

            pygame.draw.line(surface, color,
                             (x, self.y + self.marker_lane_height),
                             (x, self.y + self.height - 24), 1)

    def _draw_playhead(self, surface):
        try:
            beat_pos = self.renderer.get_playhead_beat()
        except Exception:
            beat_pos = 0

        self.playhead_x = self._beat_to_x(beat_pos)

        glow_height = self.height - self.marker_lane_height - 24
        glow_surf = pygame.Surface((10, glow_height), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (255, 60, 60, 90), glow_surf.get_rect(), border_radius=4)
        surface.blit(glow_surf, (self.playhead_x - 5, self.y + self.marker_lane_height))

        pygame.draw.line(surface, (255, 80, 80),
                         (self.playhead_x, self.y + self.marker_lane_height),
                         (self.playhead_x, self.y + self.height - 24), 2)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        self._draw_background(surface)
        self._draw_marker_lane(surface)
        self._draw_beats(surface)
        self._draw_bars(surface)
        self._draw_selection_region(surface)
        self._draw_loop_region(surface)
        self._draw_playhead(surface)
        self._draw_zoom_bar(surface)
        self._draw_scroll_bar(surface)

    # ---------------------------------------------------------
    # ZOOM & SCROLL
    # ---------------------------------------------------------
    def _apply_zoom(self, mouse_x, delta):
        old_zoom = self.zoom

        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1

        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

        rel_x = mouse_x - self.x
        scale = self.zoom / old_zoom
        self.scroll_x = int((self.scroll_x + rel_x) * scale - rel_x)

        self.scroll_x = max(0, min(self.scroll_x, 100000))

    def _apply_scroll(self, delta):
        self.scroll_x += delta * 40
        self.scroll_x = max(0, min(self.scroll_x, 100000))

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()

        # Wheel events
        if event.type == pygame.MOUSEWHEEL:
            if self.zoom_bar_rect.collidepoint(mx, my):
                return None
            if self.scroll_bar_rect.collidepoint(mx, my):
                return None

            if not (self.x <= mx <= self.x + self.width):
                return None
            if not (self.y <= my <= self.y + self.height):
                return None

            mods = pygame.key.get_mods()
            ctrl = mods & pygame.KMOD_CTRL
            shift = mods & pygame.KMOD_SHIFT

            if ctrl:
                self._apply_zoom(mx, event.y)
                return {"zoom": self.zoom}

            if shift:
                self._apply_scroll(-event.y)
                return {"scroll": self.scroll_x}

            self._apply_scroll(-event.y * 5)
            return {"scroll": self.scroll_x}

        # -----------------------------------------------------
        # ZOOM BAR – DRAG
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.zoom_bar_rect.collidepoint(mx, my):
                self.zoom_thumb_dragging = True
                return {"zoom_bar_drag_start": True}

        if event.type == pygame.MOUSEMOTION:
            if self.zoom_thumb_dragging:
                rel = mx - self.zoom_bar_rect.x
                t = rel / (self.zoom_bar_rect.width - self.zoom_thumb_width)
                t = max(0.0, min(1.0, t))
                self.zoom = self.min_zoom + t * (self.max_zoom - self.min_zoom)
                return {"zoom_bar_drag": self.zoom}

        if event.type == pygame.MOUSEBUTTONUP:
            self.zoom_thumb_dragging = False

        # -----------------------------------------------------
        # SCROLL BAR – DRAG
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.scroll_bar_rect.collidepoint(mx, my):
                if self.scroll_thumb_rect.collidepoint(mx, my):
                    self.scroll_thumb_dragging = True
                    self.scroll_thumb_offset = mx - self.scroll_thumb_rect.x
                    return {"scroll_drag_start": True}

        if event.type == pygame.MOUSEMOTION:
            if self.scroll_thumb_dragging:
                new_x = mx - self.scroll_thumb_offset
                new_x = max(self.scroll_bar_rect.x,
                            min(new_x, self.scroll_bar_rect.right - self.scroll_thumb_rect.width))

                t = (new_x - self.scroll_bar_rect.x) / (self.scroll_bar_rect.width - self.scroll_thumb_rect.width)

                total_width = 800 * self.pixels_per_beat * self.zoom
                max_scroll = max(1, total_width - self.width)

                self.scroll_x = int(t * max_scroll)
                return {"scroll_drag": self.scroll_x}

        if event.type == pygame.MOUSEBUTTONUP:
            self.scroll_thumb_dragging = False

        # -----------------------------------------------------
        # MARKER LANE
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.y <= my <= self.y + self.marker_lane_height:
                beat = self._x_to_beat(mx)

                for i, marker in enumerate(self.markers):
                    x = self._beat_to_x(marker["beat"])
                    if abs(mx - x) < 8:
                        self.selected_marker = i
                        self.marker_dragging = True
                        self.marker_drag_offset = beat - marker["beat"]
                        return {"marker_select": i}

                new_marker = {"beat": beat, "label": str(len(self.markers) + 1)}
                self.markers.append(new_marker)
                self.selected_marker = len(self.markers) - 1

                self.event_bus.emit("marker_added", beat, new_marker["label"])
                return {"marker_added": beat}

        if event.type == pygame.MOUSEMOTION:
            if self.marker_dragging and self.selected_marker is not None:
                beat = self._x_to_beat(mx)
                self.markers[self.selected_marker]["beat"] = beat - self.marker_drag_offset
                return {"marker_drag": True}

        if event.type == pygame.MOUSEBUTTONUP:
            self.marker_dragging = False

        # Delete marker
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DELETE:
            if self.selected_marker is not None:
                removed = self.markers.pop(self.selected_marker)
                self.event_bus.emit("marker_deleted", removed["beat"], removed["label"])
                self.selected_marker = None
                return {"marker_deleted": True}

        # -----------------------------------------------------
        # SELECTION REGION
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.y + self.marker_lane_height <= my <= self.y + self.height - 24:

                beat = self._x_to_beat(mx)

                if self.sel_start is not None and self.sel_end is not None:
                    x1 = self._beat_to_x(self.sel_start)
                    x2 = self._beat_to_x(self.sel_end)

                    if abs(mx - x1) < 6:
                        self.sel_resizing_left = True
                        return {"sel_resize_left": True}

                    if abs(mx - x2) < 6:
                        self.sel_resizing_right = True
                        return {"sel_resize_right": True}

                    if x1 < mx < x2:
                        self.sel_dragging = True
                        self.sel_drag_offset = beat - self.sel_start
                        return {"sel_drag": True}

                self.sel_start = beat
                self.sel_end = beat
                self.sel_resizing_right = True
                self.event_bus.emit("selection_start", beat)
                return {"sel_start": beat}

        if event.type == pygame.MOUSEMOTION:
            if self.sel_resizing_left and self.sel_start is not None:
                beat = self._x_to_beat(mx)
                self.sel_start = beat
                self.event_bus.emit("selection_change", self.sel_start, self.sel_end)
                return {"sel_resize_left_drag": True}

            if self.sel_resizing_right and self.sel_end is not None:
                beat = self._x_to_beat(mx)
                self.sel_end = beat
                self.event_bus.emit("selection_change", self.sel_start, self.sel_end)
                return {"sel_resize_right_drag": True}

            if self.sel_dragging and self.sel_start is not None and self.sel_end is not None:
                beat = self._x_to_beat(mx)
                length = self.sel_end - self.sel_start
                self.sel_start = beat - self.sel_drag_offset
                self.sel_end = self.sel_start + length
                self.event_bus.emit("selection_change", self.sel_start, self.sel_end)
                return {"sel_drag_move": True}

        if event.type == pygame.MOUSEBUTTONUP:
            if self.sel_resizing_left or self.sel_resizing_right or self.sel_dragging:
                self.sel_resizing_left = False
                self.sel_resizing_right = False
                self.sel_dragging = False
                self.event_bus.emit("selection_end", self.sel_start, self.sel_end)
                return {"sel_end": True}

        # -----------------------------------------------------
        # LOOP REGION
        # -----------------------------------------------------
        if event.type
