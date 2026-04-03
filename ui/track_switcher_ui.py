import pygame
import math

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
        self.record_arm = [False] * self.track_count

        self.volume = [1.0] * self.track_count
        self.pan = [0.0] * self.track_count

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

    def _any_solo(self):
        return any(self.solo)

    def _is_audible(self, index):
        if not self.active_tracks[index]:
            return False
        if self.mute[index]:
            return False
        if self._any_solo() and not self.solo[index]:
            return False
        return True

    def _emit_audible_state(self):
        any_solo = self._any_solo()
        for i in range(self.track_count):
            audible = self._is_audible(i)
            self.event_bus.emit("track_audible_state", i, audible, any_solo)

    def draw(self, surface, active_track=None):
        any_solo = self._any_solo()

        for i in range(self.track_count):
            base_color = self.track_colors[i]
            rect = pygame.Rect(
                i * self.button_width,
                0,
                self.button_width,
                self.button_height
            )

            if self.mute[i]:
                color = (120, 120, 120)
            elif any_solo:
                if self.solo[i]:
                    color = (255, 255, 120)
                else:
                    color = (80, 80, 80)
            else:
                if self.solo[i]:
                    color = (255, 255, 120)
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

            vol_h = int(self.volume[i] * 30)
            vol_rect = pygame.Rect(
                i * self.button_width + 6,
                self.button_height - 60,
                self.button_width - 12,
                vol_h
            )
            pygame.draw.rect(surface, (180, 180, 255), vol_rect)

            pan_x = i * self.button_width + self.button_width // 2
            pan_y = self.button_height - 75
            pygame.draw.circle(surface, (50, 50, 50), (pan_x, pan_y), 6)
            angle = self.pan[i] * math.pi
            line_x = pan_x + int(6 * math.sin(angle))
            line_y = pan_y - int(6 * math.cos(angle))
            pygame.draw.line(surface, (255, 255, 255), (pan_x, pan_y), (line_x, line_y), 2)

            rec_rect = pygame.Rect(
                i * self.button_width + 10,
                self.button_height - 90,
                self.button_width - 20,
                10
            )
            if self.record_arm[i]:
                pygame.draw.rect(surface, (255, 0, 0), rec_rect)
            else:
                pygame.draw.rect(surface, (80, 0, 0), rec_rect)

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

                    if local_y >= self.button_height - 90 and local_y < self.button_height - 80:
                        self.record_arm[index] = not self.record_arm[index]
                        self.event_bus.emit("track_record_arm", index, self.record_arm[index])
                        return {"record_arm": index}

                    if local_y >= self.button_height - 60 and local_y < self.button_height - 30:
                        rel = (local_y - (self.button_height - 60)) / 30
                        self.volume[index] = max(0.0, min(1.0, rel))
                        self.event_bus.emit("track_volume", index, self.volume[index])
                        return {"volume": index}

                    if local_y >= self.button_height - 75 and local_y < self.button_height - 65:
                        rel = (mx - (self.x + index * self.button_width)) / self.button_width
                        self.pan[index] = max(-1.0, min(1.0, (rel - 0.5) * 2))
                        self.event_bus.emit("track_pan", index, self.pan[index])
                        return {"pan": index}

                    if local_y >= self.button_height - 22 and local_y < self.button_height - 12:
                        self.mute[index] = not self.mute[index]
                        self.event_bus.emit("track_mute", index, self.mute[index])
                        self._emit_audible_state()
                        return {"mute": index}

                    if local_y >= self.button_height - 12:
                        self.solo[index] = not self.solo[index]
                        self.event_bus.emit("track_solo", index, self.solo[index])
                        self._emit_audible_state()
                        return {"solo": index}

                    self.active_tracks[index] = not self.active_tracks[index]
                    self.event_bus.emit("track_toggle", index, self.active_tracks[index])
                    self.event_bus.emit("track_selected", index)
                    self._emit_audible_state()
                    return {"selected_track": index}

        return None
