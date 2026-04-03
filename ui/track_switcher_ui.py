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

        self.track_activity = [0.0] * self.track_count
        self.peak_hold = [0.0] * self.track_count

        self.font = pygame.font.Font(None, 14)

    def update_activity(self, activity_dict):
        for i in range(self.track_count):
            try:
                level = activity_dict.get(i, 0.0)
                self.track_activity[i] = level

                if level > self.peak_hold[i]:
                    self.peak_hold[i] = level
                else:
                    self.peak_hold[i] = max(0.0, self.peak_hold[i] - 0.01)

            except Exception:
                self.track_activity[i] = 0.0

    def draw(self, surface, active_track=None):
        for i in range(self.track_count):
            base_color = self.track_colors[i]
            rect = pygame.Rect(
                i * self.button_width,
                0,
                self.button_width,
                self.button_height
            )

            if self.solo[i]:
                color = (255, 255, 120)
            elif self.mute[i]:
                color = (120, 120, 120)
            else:
                color = base_color

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            if active_track == i:
                pygame.draw.rect(surface, (255, 255, 255), rect, 4)

            level = self.track_activity[i]
            if level > 0:
                meter_height = int(level * 20)
                meter_rect = pygame.Rect(
                    i * self.button_width + 4,
                    2,
                    self.button_width - 8,
                    meter_height
                )
                pygame.draw.rect(surface, (0, 255, 0), meter_rect)

            peak = self.peak_hold[i]
            if peak > 0:
                peak_y = 2 + int(peak * 20)
                peak_rect = pygame.Rect(
                    i * self.button_width + 4,
                    peak_y,
                    self.button_width - 8,
                    2
                )
                pygame.draw.rect(surface, (255, 255, 255), peak_rect)

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
