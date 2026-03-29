import pygame

class TrackManagerUI:
    def __init__(self, width, height, track_system):
        self.width = width
        self.height = height
        self.track_system = track_system

        pygame.font.init()
        self.font = pygame.font.SysFont("Arial", 20, bold=True)

        self.button_width = 70
        self.button_height = 40
        self.margin = 10

        self._generate_buttons()

    def _generate_buttons(self):
        self.buttons = []
        track_count = len(self.track_system.tracks)

        for track_id in range(track_count):
            x = 20 + track_id * (self.button_width + self.margin)
            y = 10

            self.buttons.append({
                "track_id": track_id,
                "x": x,
                "y": y,
                "w": self.button_width,
                "h": self.button_height
            })

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos

            for btn in self.buttons:
                x, y, w, h = btn["x"], btn["y"], btn["w"], btn["h"]

                if x <= mx <= x + w and y <= my <= y + h:
                    track_id = btn["track_id"]

                    current = self.track_system.is_visible(track_id)
                    self.track_system.set_visible(track_id, not current)

                    self.track_system.set_active_track(track_id)

    def draw(self, surface):
        active_id = self.track_system.get_active_track()

        for btn in self.buttons:
            track_id = btn["track_id"]
            x, y, w, h = btn["x"], btn["y"], btn["w"], btn["h"]

            color = self.track_system.get_color(track_id)

            if not self.track_system.is_visible(track_id):
                color = (color[0] // 3, color[1] // 3, color[2] // 3)

            border_color = (255, 255, 255) if track_id == active_id else (80, 80, 80)
            border_width = 4 if track_id == active_id else 2

            pygame.draw.rect(surface, color, (x, y, w, h), border_radius=6)
            pygame.draw.rect(surface, border_color, (x, y, w, h), border_width, border_radius=6)

            text = self.font.render(str(track_id + 1), True, (0, 0, 0))
            surface.blit(text, (x + w // 2 - text.get_width() // 2, y + h // 2 - text.get_height() // 2))
