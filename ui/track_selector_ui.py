import pygame

class TrackSelectorUI:
    def __init__(self, track_system, width=1400, height=60):
        self.track_system = track_system
        self.width = width
        self.height = height

        self.button_width = 60
        self.button_height = 40
        self.margin = 10

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 20, bold=True)
        except Exception:
            self.font = None

        self._generate_buttons()

    def _generate_buttons(self):
        self.track_buttons = []

        try:
            track_count = len(getattr(self.track_system, "tracks", {}))
        except Exception:
            track_count = 0

        for i in range(track_count):
            track_id = i
            x = self.margin + i * (self.button_width + self.margin)
            y = 10

            try:
                rect = pygame.Rect(x, y, self.button_width, self.button_height)
            except Exception:
                continue

            self.track_buttons.append({
                "id": track_id,
                "rect": rect
            })

    def handle_click(self, pos):
        if not isinstance(pos, (tuple, list)) or len(pos) != 2:
            return None

        for btn in self.track_buttons:
            rect = btn.get("rect")
            track_id = btn.get("id")

            if rect is None or track_id is None:
                continue

            try:
                if rect.collidepoint(pos):
                    try:
                        current = self.track_system.is_visible(track_id)
                        self.track_system.set_visible(track_id, not current)
                    except Exception:
                        pass

                    try:
                        self.track_system.set_active_track(track_id)
                    except Exception:
                        pass

                    return track_id
            except Exception:
                continue

        return None

    def draw(self, surface):
        if surface is None:
            return

        try:
            active_id = self.track_system.get_active_track()
        except Exception:
            active_id = None

        for btn in self.track_buttons:
            track_id = btn.get("id")
            rect = btn.get("rect")

            if rect is None or track_id is None:
                continue

            try:
                color = self.track_system.get_color(track_id)
                if not (
                    isinstance(color, (tuple, list)) and
                    len(color) == 3 and
                    all(isinstance(c, int) for c in color)
                ):
                    color = (255, 255, 255)
            except Exception:
                color = (255, 255, 255)

            try:
                if not self.track_system.is_visible(track_id):
                    color = (color[0] // 3, color[1] // 3, color[2] // 3)
            except Exception:
                pass

            try:
                is_active = (track_id == active_id)
            except Exception:
                is_active = False

            border_color = (255, 255, 255) if is_active else (80, 80, 80)
            border_width = 4 if is_active else 2

            try:
                pygame.draw.rect(surface, color, rect)
                pygame.draw.rect(surface, border_color, rect, border_width)
            except Exception:
                continue

            try:
                if self.font:
                    text_surface = self.font.render(str(track_id + 1), True, (0, 0, 0))
                    text_rect = text_surface.get_rect(center=rect.center)
                    surface.blit(text_surface, text_rect)
            except Exception:
                pass
