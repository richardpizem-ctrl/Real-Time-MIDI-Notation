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

        self.controller.set_bounds(w, h)
        self._recompute_bars()

    def _recompute_bars(self):
        """Prepočíta pozície zoom a scroll barov podľa aktuálnej veľkosti."""
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
        """Vypočíta pozíciu a veľkosť scrollbar handle podľa zoomu a scrollu."""
        total_width = 200000  # virtuálna šírka timeline
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
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        # 1. TimelineController vykreslí grid + playhead
        timeline_surface = self.controller.render()
        if timeline_surface is not None:
            surface.blit(timeline_surface, (self.x, self.y))

        # 2. RULER (taktové čísla + beat tick lines)
        self._draw_ruler(surface)

        # 3. UI overlay (zoom bar, scroll bar)
        self._draw_zoom_bar(surface)
        self._draw_scroll_bar(surface)

        # 4. HANDLE
        handle = self._compute_handle_rect()
        pygame.draw.rect(surface, (120, 120, 130), handle)

    # ---------------------------------------------------------
    # RULER DRAW (NOVÉ)
    # ---------------------------------------------------------
    def _draw_ruler(self, surface):
        if not self.font:
            return

        beats_per_bar = self.controller.beats_per_bar
        layout = self.controller.layout

        # Ruler height (top 20 px)
        ruler_y = self.y
        ruler_h = 20

        # Background
        pygame.draw.rect(surface, (35, 35, 40), (self.x, ruler_y, self.width, ruler_h))

        # Visible beat range
        start_beat = layout.pixel_to_beat(self.scroll_x)
        end_beat = layout.pixel_to_beat(self.scroll_x + self.width)

        start_beat = int(start_beat) - 2
        end_beat = int(end_beat) + 2

        for beat in range(start_beat, end_beat):
            if beat < 0:
                continue

            px = self.x + layout.beat_to_pixel(beat) - self.scroll_x

            # Taktová čiara
            if beat % beats_per_bar == 0:
                pygame.draw.line(surface, (180, 180, 190), (px, ruler_y), (px, ruler_y + ruler_h), 2)

                bar_number = beat // beats_per_bar + 1
                text = self.font.render(str(bar_number), True, (220, 220, 230))
                surface.blit(text, (px + 4, ruler_y + 2))

            # Beat tick
            else:
                pygame.draw.line(surface, (110, 110, 120), (px, ruler_y + 10), (px, ruler_y + ruler_h), 1)

    # ---------------------------------------------------------
    # ZOOM & SCROLL
    # ---------------------------------------------------------
    def _apply_zoom(self, mouse_x, delta):
        old_zoom = self.zoom

        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1

        self.zoom = max(0.25, min(4.0, self.zoom))

        self.controller.layout.set_zoom(self.zoom)

        if self.renderer and hasattr(self.renderer, "set_zoom"):
            try:
                self.renderer.set_zoom(self.zoom)
            except:
                pass

        rel_x = mouse_x - self.x
        scale = self.zoom / old_zoom
        self.scroll_x = int((self.scroll_x + rel_x) * scale - rel_x)
        self.scroll_x = max(0, min(self.scroll_x, 100000))

        self.controller.layout.set_offset(self.scroll_x)

        if self.renderer and hasattr(self.renderer, "set_scroll_offset"):
            try:
                self.renderer.set_scroll_offset(self.scroll_x)
            except:
                pass

    def _apply_scroll(self, delta):
        self.scroll_x += delta * 40
        self.scroll_x = max(0, min(self.scroll_x, 100000))
        self.controller.layout.set_offset(self.scroll_x)

        if self.renderer and hasattr(self.renderer, "set_scroll_offset"):
            try:
                self.renderer.set_scroll_offset(self.scroll_x)
            except:
                pass

    # ---------------------------------------------------------
    # CLICK‑TO‑SEEK
    # ---------------------------------------------------------
    def _apply_seek(self, mouse_x):
        local_x = mouse_x - self.x
        beat = self.controller.layout.pixel_to_beat(local_x)
        time_sec = self.controller.beat_to_seconds(beat)

        try:
            self.controller.set_playhead_position(time_sec)
        except:
            pass

        if self.renderer and hasattr(self.renderer, "set_playback_time"):
            try:
                self.renderer.set_playback_time(time_sec)
            except:
                pass

        return {"seek": time_sec}

    # ---------------------------------------------------------
    # DRAG‑SCROLL (pravé tlačidlo)
    # ---------------------------------------------------------
    def _start_drag(self, mouse_x):
        self.dragging = True
        self.drag_start_x = mouse_x
        self.drag_initial_scroll = self.scroll_x

    def _update_drag(self, mouse_x):
        if not self.dragging:
            return

        dx = mouse_x - self.drag_start_x
        self.scroll_x = max(0, min(self.drag_initial_scroll - dx, 100000))

        self.controller.layout.set_offset(self.scroll_x)

        if self.renderer and hasattr(self.renderer, "set_scroll_offset"):
            try:
                self.renderer.set_scroll_offset(self.scroll_x)
            except:
                pass

    def _end_drag(self):
        self.dragging = False

    # ---------------------------------------------------------
    # HANDLE DRAG
    # ---------------------------------------------------------
    def _start_handle_drag(self, mouse_x):
        self.handle_dragging = True
        handle = self._compute_handle_rect()
        self.handle_drag_offset = mouse_x - handle.x

    def _update_handle_drag(self, mouse_x):
        if not self.handle_dragging:
            return

        handle = self._compute_handle_rect()
        new_x = mouse_x - self.handle_drag_offset

        new_x = max(self.x, min(new_x, self.x + self.width - handle.w))

        scroll_ratio = (new_x - self.x) / (self.width - handle.w)
        total_width = 200000 * self.zoom
        max_scroll = max(0, total_width - self.width)

        self.scroll_x = int(scroll_ratio * max_scroll)

        self.controller.layout.set_offset(self.scroll_x)

        if self.renderer and hasattr(self.renderer, "set_scroll_offset"):
            try:
                self.renderer.set_scroll_offset(self.scroll_x)
            except:
                pass

    def _end_handle_drag(self):
        self.handle_dragging = False

    # ---------------------------------------------------------
    # ZOOM BAR DRAW
    # ---------------------------------------------------------
    def _draw_zoom_bar(self, surface):
        pygame.draw.rect(surface, (60, 60, 65), self.zoom_bar_rect)

    # ---------------------------------------------------------
    # SCROLL BAR DRAW
    # ---------------------------------------------------------
    def _draw_scroll_bar(self, surface):
        pygame.draw.rect(surface, (50, 50, 55), self.scroll_bar_rect)

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        mx, my = pygame.mouse.get_pos()

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
