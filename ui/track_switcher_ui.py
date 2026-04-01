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

    def draw(self, surface, active_track=None):
        for i in range(self.track_count):
            color = self.track_colors[i]
            rect = pygame.Rect(
                i * self.button_width,
                0,
                self.button_width,
                self.button_height
            )

            # Background based on ON/OFF
            if self.active_tracks[i]:
                pygame.draw.rect(surface, color, rect)
            else:
                pygame.draw.rect(surface, (60, 60, 60), rect)

            # Normal border
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            # ACTIVE TRACK HIGHLIGHT (NEW)
            if active_track == i:
                pygame.draw.rect(surface, (255, 255, 255), rect, 4)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            # Check vertical bounds
            if 0 <= my - self.y <= self.button_height:
                index = (mx - self.x) // self.button_width

                if 0 <= index < self.track_count:
                    # Toggle ON/OFF
                    self.active_tracks[index] = not self.active_tracks[index]
                    self.event_bus.emit("track_toggle", index, self.active_tracks[index])

                    # Emit track selection (NEW)
                    self.event_bus.emit("track_selected", index)

                    # Return selection to UIManager
                    return {"selected_track": index}

        return None
