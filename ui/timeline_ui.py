import pygame
import math


class TimelineUI:
    """
    Timeline UI – DAW‑štýlová časová os.
    Obsahuje:
    - pozadie
    - taktové čiary
    - beat grid
    - playback head
    - zoom (Ctrl + wheel)
    - scroll (Shift + wheel)
    - zoom na kurzor
    - loop region (klik + ťah)
    - marker lane (klik + drag + delete)
    """

    def __init__(self, x, y, width, height, event_bus, renderer):
        pygame.font.init()

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

        # Grid nastavenia
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
        self.markers = []  # list of dicts: {"beat": float, "label": str}
        self.selected_marker = None
        self.marker_dragging = False
        self.marker_drag_offset = 0

        # Font
        try:
            self.font = pygame.font.Font(None, 16)
        except Exception:
            self.font = None

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
    # DRAW HELPERS
    # ---------------------------------------------------------
    def _draw_background(self, surface):
        pygame.draw.rect(surface, (30, 30, 30), (self.x, self.y, self.width, self.height))

    def _draw_marker_lane(self, surface):
        lane_rect = pygame.Rect(self.x, self.y, self.width, self.marker_lane_height)
        pygame.draw.rect(surface, (45, 45, 45), lane_rect)

        for i, marker in enumerate(self.markers):
            x = self._beat_to_x(marker["beat"])
            if x < self.x - 20 or x > self.x + self.width + 20:
                continue

            # Marker body
            color = (255, 200, 0) if i == self.selected_marker else (255, 170, 0)
            pygame.draw.rect(surface, color, (x - 5, self.y + 5, 10, 15), border_radius=3)

            # Label
            if self.font:
                txt = self.font.render(marker["label"], True, (0, 0, 0))
                surface.blit(txt, (x - txt.get_width() // 2, self.y + 6))

    def _draw_bars(self, surface):
        total_bars = 200
        for bar in range(total_bars):
            x = self._bar_to_x(bar)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            pygame.draw.line(surface, (200, 200, 200), (x, self.y + self.marker_lane_height),
                             (x, self.y + self.height), 2)

            if self.font:
                txt = self.font.render(str(bar + 1), True, (220, 220, 220))
                surface.blit(txt, (x + 4, self.y + self.marker_lane_height + 4))

    def _draw_beats(self, surface):
        total_beats = 800
        for beat in range(total_beats):
            x = self._beat_to_x(beat)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            color = (100, 100, 100) if beat % self.beats_per_bar else (150, 150, 150)
            pygame.draw.line(surface, color,
                             (x, self.y + self.marker_lane_height),
                             (x, self.y + self.height), 1)

    def _draw_playhead(self, surface):
        try:
            beat_pos = self.renderer.get_playhead_beat()
        except Exception:
            beat_pos = 0

        self.playhead_x = self._beat_to_x(beat_pos)

        pygame.draw.line(surface, (255, 0, 0),
                         (self.playhead_x, self.y + self.marker_lane_height),
                         (self.playhead_x, self.y + self.height), 2)

    # ---------------------------------------------------------
    # LOOP REGION DRAW
    # ---------------------------------------------------------
    def _draw_loop_region(self, surface):
        if self.loop_start is None or self.loop_end is None:
            return

        x1 = self._beat_to_x(self.loop_start)
        x2 = self._beat_to_x(self.loop_end)

        if x2 < x1:
            x1, x2 = x2, x1

        rect = pygame.Rect(x1, self.y + self.marker_lane_height,
                           x2 - x1, self.height - self.marker_lane_height)

        overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        overlay.fill((0, 120, 255, 60))
        surface.blit(overlay, (rect.x, rect.y))

        pygame.draw.rect(surface, (0, 150, 255), rect, 2)

        pygame.draw.rect(surface, (0, 180, 255), (x1 - 3, rect.y, 6, rect.height))
        pygame.draw.rect(surface, (0, 180, 255), (x2 - 3, rect.y, 6, rect.height))

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        self._draw_background(surface)
        self._draw_marker_lane(surface)
        self._draw_beats(surface)
        self._draw_bars(surface)
        self._draw_loop_region(surface)
        self._draw_playhead(surface)

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
        # MARKER LANE – CLICK / DRAG / DELETE
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.y <= my <= self.y + self.marker_lane_height:
                beat = self._x_to_beat(mx)

                # Check if clicking existing marker
                for i, marker in enumerate(self.markers):
                    x = self._beat_to_x(marker["beat"])
                    if abs(mx - x) < 8:
                        self.selected_marker = i
                        self.marker_dragging = True
                        self.marker_drag_offset = beat - marker["beat"]
                        return {"marker_select": i}

                # Otherwise create new marker
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
        # LOOP REGION – CLICK / DRAG
        # -----------------------------------------------------
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not (self.x <= mx <= self.x + self.width):
                return None
            if not (self.y + self.marker_lane_height <= my <= self.y + self.height):
                return None

            beat = self._x_to_beat(mx)

            if self.loop_start is not None and self.loop_end is not None:
                x1 = self._beat_to_x(self.loop_start)
                x2 = self._beat_to_x(self.loop_end)

                if abs(mx - x1) < 6:
                    self.loop_resizing_left = True
                    return {"loop_resize_left": True}

                if abs(mx - x2) < 6:
                    self.loop_resizing_right = True
                    return {"loop_resize_right": True}

                if x1 < mx < x2:
                    self.loop_dragging = True
                    self.loop_drag_offset = beat - self.loop_start
                    return {"loop_drag": True}

            self.loop_start = beat
            self.loop_end = beat
            self.loop_resizing_right = True
            return {"loop_start": beat}

        if event.type == pygame.MOUSEMOTION:
            if self.loop_resizing_left:
                self.loop_start = self._x_to_beat(mx)
                return {"loop_resize_left": self.loop_start}

            if self.loop_resizing_right:
                self.loop_end = self._x_to_beat(mx)
                return {"loop_resize_right": self.loop_end}

            if self.loop_dragging:
                beat = self._x_to_beat(mx)
                length = self.loop_end - self.loop_start
                self.loop_start = beat - self.loop_drag_offset
                self.loop_end = self.loop_start + length
                return {"loop_drag_move": True}

        if event.type == pygame.MOUSEBUTTONUP:
            if self.loop_start is not None and self.loop_end is not None:
                try:
                    self.renderer.set_loop(self.loop_start, self.loop_end)
                except Exception:
                    pass

                self.event_bus.emit("loop_region", self.loop_start, self.loop_end)

            self.loop_dragging = False
            self.loop_resizing_left = False
            self.loop_resizing_right = False

        return None
