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

        # UI zoom/scroll (naviazané na controller.layout)
        self.zoom = 1.0
        self.scroll_x = 0

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
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        # 1. TimelineController vykreslí grid + playhead
        timeline_surface = self.controller.render()
        if timeline_surface is not None:
            surface.blit(timeline_surface, (self.x, self.y))

        # 2. UI overlay (zoom bar, scroll bar)
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

        self.zoom = max(0.25, min(4.0, self.zoom))

        # Prepojiť s controller
        self.controller.layout.set_zoom(self.zoom)

        # ---------------------------------------------------------
        # PREPOJENIE ZOOM → GraphicNotationRenderer
        # ---------------------------------------------------------
        if self.renderer and hasattr(self.renderer, "set_zoom"):
            try:
                self.renderer.set_zoom(self.zoom)
            except:
                pass
        # ---------------------------------------------------------

        # Scroll korekcia
        rel_x = mouse_x - self.x
        scale = self.zoom / old_zoom
        self.scroll_x = int((self.scroll_x + rel_x) * scale - rel_x)
        self.scroll_x = max(0, min(self.scroll_x, 100000))

        self.controller.layout.set_offset(self.scroll_x)

        # ---------------------------------------------------------
        # PREPOJENIE OFFSET → GraphicNotationRenderer
        # ---------------------------------------------------------
        if self.renderer and hasattr(self.renderer, "set_scroll_offset"):
            try:
                self.renderer.set_scroll_offset(self.scroll_x)
            except:
                pass
        # ---------------------------------------------------------

    def _apply_scroll(self, delta):
        self.scroll_x += delta * 40
        self.scroll_x = max(0, min(self.scroll_x, 100000))
        self.controller.layout.set_offset(self.scroll_x)

        # ---------------------------------------------------------
        # PREPOJENIE OFFSET → GraphicNotationRenderer
        # ---------------------------------------------------------
        if self.renderer and hasattr(self.renderer, "set_scroll_offset"):
            try:
                self.renderer.set_scroll_offset(self.scroll_x)
            except:
                pass
        # ---------------------------------------------------------

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
