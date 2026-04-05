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

        # Peak hold vizuál
        self.peak_hold = [0.0] * self.track_count

        self.font = pygame.font.Font(None, 14)

    # ---------------------------------------------------------
    # UPDATE PEAK HOLD
    # ---------------------------------------------------------
    def update_peak_hold(self):
        tm = self.event_bus.track_manager

        for i in range(self.track_count):
            tid = i + 1
            level = tm.get_activity(tid)

            if level > self.peak_hold[i]:
                self.peak_hold[i] = level
            else:
                self.peak_hold[i] = max(0.0, self.peak_hold[i] - 0.01)

    # ---------------------------------------------------------
    # SOLO / AUDIBLE LOGIC
    # ---------------------------------------------------------
    def _any_solo(self):
        return any(self.event_bus.track_manager.solo.values())

    def _emit_audible_state(self):
        tm = self.event_bus.track_manager
        any_solo = self._any_solo()

        for i in range(self.track_count):
            tid = i + 1
            audible = tm.is_effectively_active(tid)
            self.event_bus.emit("track_audible_state", i, audible, any_solo)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface, active_track=None):
        tm = self.event_bus.track_manager
        any_solo = self._any_solo()

        self.update_peak_hold()

        for i in range(self.track_count):
            tid = i + 1
            base_color = self.track_colors[i]

            rect = pygame.Rect(
                self.x + i * self.button_width,
                self.y,
                self.button_width,
                self.button_height
            )

            # COLOR LOGIC
            if tm.is_muted(tid):
                color = (120, 120, 120)
            elif any_solo:
                if tm.is_solo(tid):
                    color = (255, 255, 120)
                else:
                    color = (80, 80, 80)
            else:
                if tm.is_solo(tid):
                    color = (255, 255, 120)
                else:
                    color = base_color

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            # ACTIVE TRACK BORDER
            if active_track == tid:
                pygame.draw.rect(surface, (255, 255, 255), rect, 3)

            # REALTIME LEVEL
            level = tm.get_activity(tid)
            if level > 0:
                meter_height = int(level * 20)
                meter_rect = pygame.Rect(
                    rect.x + 4,
                    rect.y + 2,
                    self.button_width - 8,
                    meter_height
                )
                pygame.draw.rect(surface, (0, 255, 0), meter_rect)

            # PEAK HOLD
            peak = self.peak_hold[i]
            if peak > 0:
                peak_y = rect.y + 2 + int(peak * 20)
                peak_rect = pygame.Rect(
                    rect.x + 4,
                    peak_y,
                    self.button_width - 8,
                    2
                )
                pygame.draw.rect(surface, (255, 255, 255), peak_rect)

            # VOLUME
            vol = tm.get_volume(tid)
            vol_h = int(vol * 30)
            vol_rect = pygame.Rect(
                rect.x + 6,
                rect.y + self.button_height - 55,
                self.button_width - 12,
                vol_h
            )
            pygame.draw.rect(surface, (180, 180, 255), vol_rect)

            # PAN
            pan_val = tm.get_pan(tid)
            pan_x = rect.x + self.button_width // 2
            pan_y = rect.y + self.button_height - 70
            pygame.draw.circle(surface, (50, 50, 50), (pan_x, pan_y), 6)
            angle = pan_val * math.pi
            line_x = pan_x + int(6 * math.sin(angle))
            line_y = pan_y - int(6 * math.cos(angle))
            pygame.draw.line(surface, (255, 255, 255), (pan_x, pan_y), (line_x, line_y), 2)

            # RECORD ARM
            rec_rect = pygame.Rect(
                rect.x + 4,
                rect.y + self.button_height - 85,
                self.button_width - 8,
                10
            )
            pygame.draw.rect(surface,
                             (255, 0, 0) if tm.is_record_armed(tid) else (80, 0, 0),
                             rec_rect)

            # MUTE
            mute_rect = pygame.Rect(
                rect.x + 4,
                rect.y + self.button_height - 20,
                self.button_width - 8,
                10
            )
            pygame.draw.rect(surface,
                             (255, 80, 80) if tm.is_muted(tid) else (100, 40, 40),
                             mute_rect)

            # SOLO
            solo_rect = pygame.Rect(
                rect.x + 4,
                rect.y + self.button_height - 10,
                self.button_width - 8,
                10
            )
            pygame.draw.rect(surface,
                             (255, 255, 80) if tm.is_solo(tid) else (100, 100, 40),
                             solo_rect)

            # NAME
            try:
                name = tm.get_name(tid)
            except Exception:
                name = f"Track {tid}"

            name_color = (255, 255, 255) if active_track == tid else (0, 0, 0)
            text_surface = self.font.render(name, True, name_color)
            text_rect = text_surface.get_rect(center=(
                rect.x + self.button_width // 2,
                rect.y + 12
            ))
            surface.blit(text_surface, text_rect)

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_event(self, event):
        tm = self.event_bus.track_manager

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()

            if not (self.x <= mx <= self.x + self.width):
                return None
            if not (self.y <= my <= self.y + self.button_height):
                return None

            index = (mx - self.x) // self.button_width
            tid = index + 1
            local_y = my - self.y

            # RECORD ARM
            if self.button_height - 85 <= local_y < self.button_height - 75:
                tm.toggle_record_arm(tid)
                self.event_bus.emit("track_record_arm", index, tm.is_record_armed(tid))
                return {"record_arm": index}

            # PAN
            if self.button_height - 75 <= local_y < self.button_height - 65:
                rel = (mx - (self.x + index * self.button_width)) / self.button_width
                tm.set_pan(tid, (rel - 0.5) * 2)
                self.event_bus.emit("track_pan", index, tm.get_pan(tid))
                return {"pan": index}

            # VOLUME
            if self.button_height - 55 <= local_y < self.button_height - 25:
                rel = (local_y - (self.button_height - 55)) / 30
                tm.set_volume(tid, rel)
                self.event_bus.emit("track_volume", index, tm.get_volume(tid))
                return {"volume": index}

            # MUTE
            if self.button_height - 20 <= local_y < self.button_height - 10:
                tm.set_mute(tid, not tm.is_muted(tid))
                self.event_bus.emit("track_mute", index, tm.is_muted(tid))
                self._emit_audible_state()
                return {"mute": index}

            # SOLO
            if local_y >= self.button_height - 10:
                tm.set_solo(tid, not tm.is_solo(tid))
                self.event_bus.emit("track_solo", index, tm.is_solo(tid))
                self._emit_audible_state()
                return {"solo": index}

            # SELECT TRACK
            tm.set_active_track(tid)
            self.event_bus.emit("track_selected", index)
            self._emit_audible_state()
            return {"selected_track": index}

        return None
