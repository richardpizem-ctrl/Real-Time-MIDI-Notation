import pygame
import math


class TimelineUI:
    """
    Timeline UI – DAW‑štýlová časová os.
    Teraz obsahuje:
    - pozadie
    - taktové čiary
    - beat grid
    - playback head
    - zoom (Ctrl + wheel)
    - scroll (Shift + wheel)
    - zoom na kurzor
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

    def _bar_to_x(self, bar_index):
        return self._beat_to_x(bar_index * self.beats_per_bar)

    # ---------------------------------------------------------
    # DRAW HELPERS
    # ---------------------------------------------------------
    def _draw_background(self, surface):
        pygame.draw.rect(surface, (30, 30, 30), (self.x, self.y, self.width, self.height))

    def _draw_bars(self, surface):
        total_bars = 200
        for bar in range(total_bars):
            x = self._bar_to_x(bar)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            pygame.draw.line(surface, (200, 200, 200), (x, self.y), (x, self.y + self.height), 2)

            if self.font:
                txt = self.font.render(str(bar + 1), True, (220, 220, 220))
                surface.blit(txt, (x + 4, self.y + 4))

    def _draw_beats(self, surface):
        total_beats = 800
        for beat in range(total_beats):
            x = self._beat_to_x(beat)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            color = (100, 100, 100) if beat % self.beats_per_bar else (150, 150, 150)
            pygame.draw.line(surface, color, (x, self.y), (x, self.y + self.height), 1)

    def _draw_playhead(self, surface):
        try:
            beat_pos = self.renderer.get_playhead_beat()
        except Exception:
            beat_pos = 0

        self.playhead_x = self._beat_to_x(beat_pos)

        pygame.draw.line(surface, (255, 0, 0), (self.playhead_x, self.y), (self.playhead_x, self.y + self.height), 2)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        self._draw_background(surface)
        self._draw_beats(surface)
        self._draw_bars(surface)
        self._draw_playhead(surface)

    # ---------------------------------------------------------
    # ZOOM & SCROLL
    # ---------------------------------------------------------
    def _apply_zoom(self, mouse_x, delta):
        old_zoom = self.zoom

        # Zoom in/out
        if delta > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1

        # Clamp
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom))

        # Zoom na kurzor
        rel_x = mouse_x - self.x
        scale = self.zoom / old_zoom
        self.scroll_x = int((self.scroll_x + rel_x) * scale - rel_x)

        # Scroll clamp
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

            # Ctrl + wheel → ZOOM
            if ctrl:
                self._apply_zoom(mx, event.y)
                return {"zoom": self.zoom}

            # Shift + wheel → SCROLL
            if shift:
                self._apply_scroll(-event.y)
                return {"scroll": self.scroll_x}

            # Default wheel → scroll jemne
            self._apply_scroll(-event.y * 5)
            return {"scroll": self.scroll_x}

        # Click → seek
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not (self.x <= mx <= self.x + self.width):
                return None
            if not (self.y <= my <= self.y + self.height):
                return None

            rel_x = mx - self.x + self.scroll_x
            beat = rel_x / (self.pixels_per_beat * self.zoom)

            try:
                self.renderer.set_playhead_beat(beat)
            except Exception:
                pass

            self.event_bus.emit("timeline_seek", beat)
            return {"seek": beat}

        return None
