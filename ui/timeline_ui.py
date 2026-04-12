import pygame
import math


class TimelineUI:
    """
    Timeline UI – základná kostra pre DAW‑štýlovú časovú os.
    Obsahuje:
    - pozadie
    - taktové čiary
    - beat grid
    - playback head
    - zoom / scroll premenné
    - marker lane (pripravené)
    - event handling pre kliky a drag
    """

    def __init__(self, x, y, width, height, event_bus, renderer):
        pygame.font.init()

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.event_bus = event_bus
        self.renderer = renderer  # GraphicNotationRenderer (nový)

        # Zoom & scroll
        self.zoom = 1.0
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
        # Taktové čiary
        total_bars = 200  # dočasné maximum
        for bar in range(total_bars):
            x = self._bar_to_x(bar)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            pygame.draw.line(surface, (200, 200, 200), (x, self.y), (x, self.y + self.height), 2)

            if self.font:
                txt = self.font.render(str(bar + 1), True, (220, 220, 220))
                surface.blit(txt, (x + 4, self.y + 4))

    def _draw_beats(self, surface):
        # Beat grid
        total_beats = 800
        for beat in range(total_beats):
            x = self._beat_to_x(beat)
            if x < self.x - 50 or x > self.x + self.width + 50:
                continue

            color = (100, 100, 100) if beat % self.beats_per_bar else (150, 150, 150)
            pygame.draw.line(surface, color, (x, self.y), (x, self.y + self.height), 1)

    def _draw_playhead(self, surface):
        # Pozícia playheadu podľa rendereru
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
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if not (self.x <= mx <= self.x + self.width):
                return None
            if not (self.y <= my <= self.y + self.height):
                return None

            # Klik na timeline → presun playheadu
            rel_x = mx - self.x + self.scroll_x
            beat = rel_x / (self.pixels_per_beat * self.zoom)

            try:
                self.renderer.set_playhead_beat(beat)
            except Exception:
                pass

            self.event_bus.emit("timeline_seek", beat)
            return {"seek": beat}

        return None
