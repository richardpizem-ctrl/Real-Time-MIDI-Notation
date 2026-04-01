import pygame

class TrackSwitcherUI:
    def __init__(self, x, y, width, height, track_colors, event_bus):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.track_colors = track_colors
        self.event_bus = event_bus

        self.track_count = 16
        self.button_width = width // self.track_count
        self.button_height = height

        self.active_tracks = [True] * self.track_count

    def draw(self, surface):
        for i in range(self.track_count):
            color = self.track_colors[i]
            rect = pygame.Rect(
                self.x + i * self.button_width,
                self.y,
                self.button_width,
                self.button_height
            )

            if self.active_tracks[i]:
                pygame.draw.rect(surface, color, rect)
            else:
                pygame.draw.rect(surface, (60, 60, 60), rect)

            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if self.y <= my <= self.y + self.button_height:
                index = (mx - self.x) // self.button_width

                if 0 <= index < self.track_count:
                    self.active_tracks[index] = not self.active_tracks[index]
                    self.event_bus.emit("track_toggle", index, self.active_tracks[index])
