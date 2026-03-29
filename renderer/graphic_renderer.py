import pygame

class GraphicNotationRenderer:
    def __init__(self, width, height, track_system):
        self.width = width
        self.height = height
        self.track_system = track_system

        self.surface = pygame.Surface((width, height))
        self.font = pygame.font.SysFont("Arial", 18)

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

        surf = pygame.Surface((self.staff_cache_width, self.staff_cache_height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))

        y_start = self.margin_top
        for i in range(5):
            y = y_start + i * self.staff_line_spacing
            pygame.draw.line(surf, (200, 200, 200), (self.margin_left, y), (self.width - 20, y), 2)

        self.staff_cache = surf
        return surf

    # ---------------------------------------------------------
    # DRAW NOTE HEAD
    # ---------------------------------------------------------
    def _draw_note(self, surface, x, y, color):
        pygame.draw.ellipse(surface, color, (x, y, 14, 10))
        pygame.draw.ellipse(surface, (0, 0, 0), (x, y, 14, 10), 2)

    # ---------------------------------------------------------
    # MAIN DRAW
    # ---------------------------------------------------------
    def draw(self, notes):
        self.surface.fill((25, 25, 25))

        # Staff lines
        staff = self._render_staff_lines()
        self.surface.blit(staff, (0, 0))

        # Draw notes
        x = self.margin_left + 10

        for note in notes:
            midi = note["note"]
            track_id = note["track_id"]

            if not self.track_system.is_visible(track_id):
                continue

            color = self.track_system.get_color(track_id)

            # Vertical position
            y = self.margin_top + (60 - midi) * 0.9

            self._draw_note(self.surface, x, y, color)
            x += self.note_spacing

        return self.surface
