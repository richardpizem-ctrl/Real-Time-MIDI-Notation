import pygame
import math

class GraphicNotationRenderer:
    def __init__(self, width, height, track_system):
        self.width = width
        self.height = height
        self.track_system = track_system

        try:
            self.surface = pygame.Surface((width, height))
        except Exception:
            self.surface = None

        try:
            self.font = pygame.font.SysFont("Arial", 18)
        except Exception:
            self.font = None

        self.staff_cache = None
        self.staff_cache_width = width
        self.staff_cache_height = 140

        self.margin_left = 40
        self.margin_top = 20
        self.note_spacing = 28
        self.staff_line_spacing = 12

        self.scroll_x = 0
        self.scroll_speed = 2.2

    # ---------------------------------------------------------
    # STAFF LINES (CACHED)
    # ---------------------------------------------------------
    def _render_staff_lines(self):
        if self.staff_cache is not None:
            return self.staff_cache

        try:
            surf = pygame.Surface(
                (self.staff_cache_width, self.staff_cache_height),
                pygame.SRCALPHA
            )
            surf.fill((0, 0, 0, 0))

            y_start = self.margin_top
            for i in range(5):
                y = y_start + i * self.staff_line_spacing
                pygame.draw.line(
                    surf,
                    (200, 200, 200),
                    (self.margin_left, y),
                    (self.width - 20, y),
                    2
                )

            self.staff_cache = surf
            return surf

        except Exception:
            return pygame.Surface((self.width, 1))

    # ---------------------------------------------------------
    # NOTE POSITIONING
    # ---------------------------------------------------------
    def _pitch_to_y(self, midi):
        try:
            return self.margin_top + (60 - midi) * 1.1
        except Exception:
            return self.margin_top

    def _time_to_x(self, timestamp):
        try:
            return self.margin_left + timestamp * self.note_spacing - self.scroll_x
        except Exception:
            return self.margin_left

    # ---------------------------------------------------------
    # DRAW NOTE HEAD
    # ---------------------------------------------------------
    def _draw_note(self, surface, x, y, color):
        try:
            pygame.draw.ellipse(surface, color, (x, y, 16, 12))
            pygame.draw.ellipse(surface, (0, 0, 0), (x, y, 16, 12), 2)
        except Exception:
            pass

    # ---------------------------------------------------------
    # MAIN DRAW
    # ---------------------------------------------------------
    def draw(self, notes):
        if self.surface is None:
            try:
                self.surface = pygame.Surface((self.width, self.height))
            except Exception:
                return None

        try:
            self.surface.fill((25, 25, 25))
        except Exception:
            pass

        try:
            staff = self._render_staff_lines()
            self.surface.blit(staff, (0, 0))
        except Exception:
            pass

        if not isinstance(notes, (list, tuple)):
            return self.surface

        # Auto-scroll
        self.scroll_x += self.scroll_speed

        # Draw notes
        for note in notes:
            if not isinstance(note, dict):
                continue

            midi = note.get("pitch") or note.get("note")
            track_id = note.get("track_id")
            timestamp = note.get("timestamp", 0)

            if midi is None or track_id is None:
                continue

            try:
                if hasattr(self.track_system, "is_visible"):
                    if not self.track_system.is_visible(track_id):
                        continue
            except Exception:
                pass

            try:
                if hasattr(self.track_system, "get_color"):
                    color = self.track_system.get_color(track_id)
                else:
                    color = (255, 255, 255)
            except Exception:
                color = (255, 255, 255)

            x = self._time_to_x(timestamp)
            y = self._pitch_to_y(midi)

            self._draw_note(self.surface, x, y, color)

        return self.surface
