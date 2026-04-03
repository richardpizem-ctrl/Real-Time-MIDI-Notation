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
        self.mute = [False] * self.track_count
        self.solo = [False] * self.track_count

        self.font = pygame.font.Font(None, 14)

    def draw(self, surface, active_track=None):
        for i in range(self.track_count):
            color = self.track_colors[i]
            rect = pygame.Rect(
                i * self.button_width,
                0,
                self.button_width,
                self.button_height
            )

            if self.active_tracks[i]:
                pygame.draw.rect(surface, color, rect)
            else:
                pygame.draw.rect(surface, (60, 60, 60), rect)

            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            if active_track == i:
                pygame.draw.rect(surface, (255, 255, 255), rect, 4)

            mute_rect = pygame.Rect(
                i * self.button_width + 4,
                self.button_height - 22,
                self.button_width - 8,
                10
            )
            solo_rect = pygame.Rect(
                i * self.button_width + 4,
                self.button_height - 12,
                self.button_width - 8,
                10
            )

            if self.mute[i]:
                pygame.draw.rect(surface, (255, 80, 80), mute_rect)
            else:
                pygame.draw.rect(surface, (100, 40, 40), mute_rect)

            if self.solo[i]:
                pygame.draw.rect(surface, (255, 255, 80), solo_rect)
            else:
                pygame.draw.rect(surface, (100, 100, 40), solo_rect)

            try:
                name = self.event_bus.track_manager.get_name(i + 1)
            except Exception:
                name = f"Track {i+1}"

            text_surface = self.font.render(name, True, (0, 0, 0))
            text_rect = text_surface.get_rect(center=(
                i * self.button_width + self.button_width // 2,
                10
            ))
            surface.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if 0 <= my - self.y <= self.button_height:
                index = (mx - self.x) // self.button_width

                if 0 <= index < self.track_count:
                    local_y = my - self.y

                    if local_y >= self.button_height - 22 and local_y < self.button_height - 12:
                        self.mute[index] = not self.mute[index]
                        self.event_bus.emit("track_mute", index, self.mute[index])
                        return {"mute": index}

                    if local_y >= self.button_height - 12:
                        self.solo[index] = not self.solo[index]
                        self.event_bus.emit("track_solo", index, self.solo[index])
                        return {"solo": index}

                    self.active_tracks[index] = not self.active_tracks[index]
                    self.event_bus.emit("track_toggle", index, self.active_tracks[index])
                    self.event_bus.emit("track_selected", index)
                    return {"selected_track": index}

        return None
