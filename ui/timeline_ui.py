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

        # ---------------------------------------------------------
        # PREPOJENIE S GraphicNotationRenderer.timeline_controller
        # ---------------------------------------------------------
        if self.renderer and hasattr(self.renderer, "timeline_controller"):
            if self.renderer.timeline_controller is not None:
                self.controller = self.renderer.timeline_controller
                Logger.info("TimelineUI: prepojené s renderer.timeline_controller")
        # ---------------------------------------------------------

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
    # LOOP REGION RECT
    # ---------------------------------------------------------
    def _compute_loop_rect(self):
        if not self.loop_active:
            return None

        layout = self.controller.layout
        px1 = self.x + layout.beat_to_pixel(self.loop_start_beat) - self.scroll_x
        px2 = self.x + layout.beat_to_pixel(self.loop_end_beat) - self.scroll_x

        if px2 < px1:
            px1, px2 = px2, px1

        return pygame.Rect(px1, self.y, px2 - px1, 20)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        # 1. Timeline grid
        timeline_surface = self.controller.render()
        if timeline_surface is not None:
            surface.blit(timeline_surface, (self.x, self.y))

        # 2. Ruler
        self._draw_ruler(surface)

        # 3. LOOP REGION
        self._draw_loop(surface)

        # 4. Bars
        self._draw_zoom_bar(surface)
        self._draw_scroll_bar(surface)

        # 5. Handle
        handle = self._compute_handle_rect()
        pygame.draw.rect(surface, (120, 120, 130), handle)

    # ---------------------------------------------------------
    # LOOP DRAW
    # ---------------------------------------------------------
    def _draw_loop(self, surface):
        rect = self._compute_loop_rect()
        if not rect:
            return

        # Loop fill
        pygame.draw.rect(surface, (80, 120, 200, 80), rect)
        # Border
        pygame.draw.rect(surface, (160, 200, 255), rect, 2)

        # Resize handles
        left = pygame.Rect(rect.x - 4, rect.y, 8, rect.h)
        right = pygame.Rect(rect.right - 4, rect.y, 8, rect.h)

        pygame.draw.rect(surface, (200, 220, 255), left)
        pygame.draw.rect(surface, (200, 220, 255), right)

    # ---------------------------------------------------------
    # RULER DRAW
    # ---------------------------------------------------------
    def _draw_ruler(self, surface):
        if not self.font:
            return

        beats_per_bar = self.controller.beats_per_bar
        layout = self.controller.layout

        ruler_y = self.y
        ruler_h = 20

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
    # LOOP REGION LOGIC
    # ---------------------------------------------------------
    def _start_loop(self, mouse_x):
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        self.loop_active = True
        self.loop_dragging = False
        self.loop_resizing_left = False
        self.loop_resizing_right = False

        self.loop_start_beat = beat
        self.loop_end_beat = beat

    def _update_loop(self, mouse_x):
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)
        self.loop_end_beat = beat

    def _finalize_loop(self):
        if self.loop_end_beat < self.loop_start_beat:
            self.loop_start_beat, self.loop_end_beat = self.loop_end_beat, self.loop_start_beat

        start_sec = self.controller.beat_to_seconds(self.loop_start_beat)
        end_sec = self.controller.beat_to_seconds(self.loop_end_beat)

        if hasattr(self.renderer, "set_loop_region"):
            try:
                self.renderer.set_loop_region(start_sec, end_sec)
            except:
                pass

        if hasattr(self.controller.layout, "set_loop"):
            try:
                self.controller.layout.set_loop(self.loop_start_beat, self.loop_end_beat)
            except:
                pass

    # ---------------------------------------------------------
    # LOOP DRAGGING
    # ---------------------------------------------------------
    def _start_loop_drag(self, mouse_x):
        layout = self.controller.layout
        rect = self._compute_loop_rect()

        self.loop_dragging = True
        self.loop_resizing_left = False
        self.loop_resizing_right = False

        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)
        self.loop_drag_offset = beat - self.loop_start_beat

    def _update_loop_drag(self, mouse_x):
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        new_start = beat - self.loop_drag_offset
        length = self.loop_end_beat - self.loop_start_beat
        new_end = new_start + length

        if new_start < 0:
            new_start = 0
            new_end = length

        self.loop_start_beat = new_start
        self.loop_end_beat = new_end

    # ---------------------------------------------------------
    # LOOP RESIZE
    # ---------------------------------------------------------
    def _start_resize_left(self, mouse_x):
        self.loop_resizing_left = True
        self.loop_resizing_right = False
        self.loop_dragging = False

    def _start_resize_right(self, mouse_x):
        self.loop_resizing_right = True
        self.loop_resizing_left = False
        self.loop_dragging = False

    def _update_resize_left(self, mouse_x):
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        if beat < 0:
            beat = 0

        if beat > self.loop_end_beat:
            beat = self.loop_end_beat

        self.loop_start_beat = beat

    def _update_resize_right(self, mouse_x):
        layout = self.controller.layout
        beat = layout.pixel_to_beat(mouse_x - self.x + self.scroll_x)

        if beat < self.loop_start_beat:
            beat = self.loop_start_beat

        self.loop_end_beat = beat

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()

        # LOOP REGION INTERACTION
        loop_rect = self._compute_loop_rect()
        if loop_rect:
            left_handle = pygame.Rect(loop_rect.x - 4, loop_rect.y, 8, loop_rect.h)
            right_handle = pygame.Rect(loop_rect.right - 4, loop_rect.y, 8, loop_rect.h)

            # LEFT RESIZE START
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if left_handle.collidepoint(mx, my):
                    self._start_resize_left(mx)
                    return None

            # RIGHT RESIZE START
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if right_handle.collidepoint(mx, my):
                    self._start_resize_right(mx)
                    return None

            # LOOP DRAG START
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if loop_rect.collidepoint(mx, my):
                    self._start_loop_drag(mx)
                    return None

            # LOOP DRAG MOVE
            if event.type == pygame.MOUSEMOTION:
                if self.loop_dragging:
                    self._update_loop_drag(mx)
                    return None

            # LOOP RESIZE MOVE
            if event.type == pygame.MOUSEMOTION:
                if self.loop_resizing_left:
                    self._update_resize_left(mx)
                    return None
                if self.loop_resizing_right:
                    self._update_resize_right(mx)
                    return None

            # LOOP END
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if self.loop_dragging or self.loop_resizing_left or self.loop_resizing_right:
                    self.loop_dragging = False
                    self.loop_resizing_left = False
                    self.loop_resizing_right = False
                    self._finalize_loop()
                    return None

        # LOOP REGION CREATION
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.y <= my <= self.y + 20:
                self._start_loop(mx)
                return None

        if event.type == pygame.MOUSEMOTION:
            if self.loop_active and pygame.mouse.get_pressed()[0]:
                self._update_loop(mx)
                return None

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

        # CLICK‑TO‑SEEK
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                return self._apply_seek(mx)

        # DRAG‑SCROLL START (pravé tlačidlo)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
            if self.x <= mx <= self.x + self.width and self.y <= my <= self.y + self.height:
                self._start_drag(mx)

        # DRAG‑SCROLL MOVE
        if event.type == pygame.MOUSEMOTION:
            if self.dragging:
                self._update_drag(mx)

        # DRAG‑SCROLL END
        if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
            self._end_drag()

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

        return None
