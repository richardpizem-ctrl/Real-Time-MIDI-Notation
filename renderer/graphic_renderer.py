import pygame

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

        # Cache staff lines
        self.staff_cache = None
        self.staff_cache_width = width
        self.staff_cache_height = 120

        # Layout
        self.margin_left = 40
        self.margin_top = 20
        self.note_spacing = 22
        self.staff_line_spacing = 12

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
    # DRAW NOTE HEAD
    # ---------------------------------------------------------
    def _draw_note(self, surface, x, y, color):
        try:
            pygame.draw.ellipse(surface, color, (x, y, 14, 10))
            pygame.draw.ellipse(surface, (0, 0, 0), (x, y, 14, 10), 2)
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

        # Staff lines
        try:
            staff = self._render_staff_lines()
            self.surface.blit(staff, (0, 0))
        except Exception:
            pass

        # Draw notes
        x = self.margin_left + 10

        if not isinstance(notes, (list, tuple)):
            return self.surface

        for note in notes:
            if not isinstance(note, dict):
                continue

            midi = note.get("pitch") or note.get("note")
            track_id = note.get("track_id")

            if midi is None or track_id is None:
                continue

            # Track visibility
            try:
                if hasattr(self.track_system, "is_visible"):
                    if not self.track_system.is_visible(track_id):
                        continue
            except Exception:
                pass

            # Track color
            try:
                if hasattr(self.track_system, "get_color"):
                    color = self.track_system.get_color(track_id)
                else:
                    color = (255, 255, 255)
            except Exception:
                color = (255, 255, 255)

            # Vertical position
            try:
                y = self.margin_top + (60 - midi) * 0.9
            except Exception:
                y = self.margin_top

            self._draw_note(self.surface, x, y, color)
            x += self.note_spacing

        return self.surface
