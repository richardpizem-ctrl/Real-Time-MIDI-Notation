import pygame
import math
from .track_control_manager import TrackControlManager


class TrackSwitcherUI:
    def __init__(
        self,
        x,
        y,
        width,
        height,
        track_colors,
        event_bus,
        track_control_manager: TrackControlManager | None = None,
    ):
        pygame.font.init()

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.track_colors = track_colors
        self.event_bus = event_bus

        # Centrálne riadenie stôp (Fáza 4)
        self.track_control_manager = track_control_manager

        self.track_count = 16
        self.button_width = max(1, width // self.track_count)
        self.button_height = height

        # Peak hold vizuál
        self.peak_hold = [0.0] * self.track_count

        try:
            self.font = pygame.font.Font(None, 14)
            self.small_font = pygame.font.Font(None, 12)
        except Exception:
            self.font = None
            self.small_font = None

    # ---------------------------------------------------------
    # UPDATE PEAK HOLD
    # ---------------------------------------------------------
    def update_peak_hold(self):
        tm = self.event_bus.track_manager

        for i in range(self.track_count):
            tid = i + 1
            try:
                level = tm.get_activity(tid)
            except Exception:
                level = 0.0

            if level > self.peak_hold[i]:
                self.peak_hold[i] = level
            else:
                self.peak_hold[i] = max(0.0, self.peak_hold[i] - 0.01)

    # ---------------------------------------------------------
    # SOLO / AUDIBLE LOGIC
    # ---------------------------------------------------------
    def _any_solo(self):
        try:
            return any(self.event_bus.track_manager.solo.values())
        except Exception:
            return False

    def _emit_audible_state(self):
        tm = self.event_bus.track_manager
        any_solo = self._any_solo()

        for i in range(self.track_count):
            tid = i + 1
            try:
                audible = tm.is_effectively_active(tid)
            except Exception:
                audible = True
            self.event_bus.emit("track_audible_state", i, audible, any_solo)

    # ---------------------------------------------------------
    # DRAW HELPERS
    # ---------------------------------------------------------
    def _draw_meter(self, surface, rect, level):
        if level <= 0:
            return
        meter_height = int(level * 20)
        meter_rect = pygame.Rect(rect.x + 4, rect.y + 2, self.button_width - 8, meter_height)
        pygame.draw.rect(surface, (0, 255, 0), meter_rect)

    def _draw_peak(self, surface, rect, peak):
        if peak <= 0:
            return
        peak_y = rect.y + 2 + int(peak * 20)
        peak_rect = pygame.Rect(rect.x + 4, peak_y, self.button_width - 8, 2)
        pygame.draw.rect(surface, (255, 255, 255), peak_rect)

    def _draw_volume(self, surface, rect, vol):
        try:
            vol = max(0.0, min(1.0, float(vol)))
        except Exception:
            vol = 0.0

        vol_h = int(vol * 30)
        vol_rect = pygame.Rect(
            rect.x + 6,
            rect.y + self.button_height - 55,
            self.button_width - 12,
            vol_h,
        )
        pygame.draw.rect(surface, (180, 180, 255), vol_rect)

        if self.small_font:
            txt = self.small_font.render("V", True, (0, 0, 0))
            surface.blit(txt, (rect.x + 2, rect.y + self.button_height - 60))

    def _draw_pan(self, surface, rect, pan_val):
        try:
            pan_val = max(-1.0, min(1.0, float(pan_val)))
        except Exception:
            pan_val = 0.0

        pan_x = rect.x + self.button_width // 2
        pan_y = rect.y + self.button_height - 70

        pygame.draw.circle(surface, (50, 50, 50), (pan_x, pan_y), 6)

        angle = pan_val * math.pi
        line_x = pan_x + int(6 * math.sin(angle))
        line_y = pan_y - int(6 * math.cos(angle))
        pygame.draw.line(surface, (255, 255, 255), (pan_x, pan_y), (line_x, line_y), 2)

        if self.small_font:
            txt = self.small_font.render("P", True, (0, 0, 0))
            surface.blit(txt, (rect.x + 2, rect.y + self.button_height - 75))

    def _draw_button(self, surface, rect, active, color_on, color_off, label):
        pygame.draw.rect(surface, color_on if active else color_off, rect)
        if self.small_font:
            txt = self.small_font.render(label, True, (0, 0, 0))
            surface.blit(txt, (rect.x + 2, rect.y + 1))

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface, active_track=None):
        tm = self.event_bus.track_manager
        any_solo = self._any_solo()

        self.update_peak_hold()

        # Aktívna stopa z TrackControlManagera
        if self.track_control_manager is not None:
            active_tid = self.track_control_manager.get_active_track() + 1
        else:
            active_tid = active_track

        for i in range(self.track_count):
            tid = i + 1

            # Farba stopy
            try:
                if self.track_control_manager is not None:
                    hex_color = self.track_control_manager.get_color(i)
                else:
                    hex_color = self.track_colors[i % len(self.track_colors)]

                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                base_color = (r, g, b)
            except Exception:
                base_color = (120, 120, 120)

            rect = pygame.Rect(
                self.x + i * self.button_width,
                self.y,
                self.button_width,
                self.button_height,
            )

            # COLOR LOGIC
            try:
                if tm.is_muted(tid):
                    color = (120, 120, 120)
                elif any_solo:
                    color = (255, 255, 120) if tm.is_solo(tid) else (80, 80, 80)
                else:
                    color = (255, 255, 120) if tm.is_solo(tid) else base_color
            except Exception:
                color = base_color

            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            # ACTIVE TRACK BORDER
            if active_tid == tid:
                pygame.draw.rect(surface, (255, 255, 255), rect, 3)

            # REALTIME LEVEL + PEAK
            self._draw_meter(surface, rect, tm.get_activity(tid))
            self._draw_peak(surface, rect, self.peak_hold[i])

            # VOLUME
            self._draw_volume(surface, rect, tm.get_volume(tid))

            # PAN
            self._draw_pan(surface, rect, tm.get_pan(tid))

            # RECORD ARM
            rec_rect = pygame.Rect(
                rect.x + 4,
                rect.y + self.button_height - 85,
                self.button_width - 8,
                10,
            )
            self._draw_button(
                surface,
                rec_rect,
                tm.is_record_armed(tid),
                (255, 0, 0),
                (80, 0, 0),
                "R",
            )

            # MUTE
            mute_rect = pygame.Rect(
                rect.x + 4,
                rect.y + self.button_height - 20,
                self.button_width - 8,
                10,
            )
            self._draw_button(
                surface,
                mute_rect,
                tm.is_muted(tid),
                (255, 80, 80),
                (100, 40, 40),
                "M",
            )

            # SOLO
            solo_rect = pygame.Rect(
                rect.x + 4,
                rect.y + self.button_height - 10,
                self.button_width - 8,
                10,
            )
            self._draw_button(
                surface,
                solo_rect,
                tm.is_solo(tid),
                (255, 255, 80),
                (100, 100, 40),
                "S",
            )

            # NAME
            try:
                name = tm.get_name(tid)
            except Exception:
                name = f"Track {tid}"

            name_color = (255, 255, 255) if active_tid == tid else (0, 0, 0)

            if self.font:
                text_surface = self.font.render(name, True, name_color)
                text_rect = text_surface.get_rect(
                    center=(rect.x + self.button_width // 2, rect.y + 12)
                )
                surface.blit(text_surface, text_rect)

    # ---------------------------------------------------------
    # PUBLIC API PRE UIManager
    # ---------------------------------------------------------
    def set_active_track(self, track_index: int):
        """UIManager volá pri zmene aktívnej stopy – no-op."""
        pass

    def update_visibility(self, track_index: int, visible: bool):
        """UIManager volá pri zmene viditeľnosti – no-op."""
        pass

    def update_color(self, track_index: int, color_hex: str):
        """UIManager volá pri zmene farby – no-op."""
        pass

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

            index = int((mx - self.x) // self.button_width)
            index = max(0, min(self.track_count - 1, index))
            tid = index + 1
            local_y = my - self.y

            mods = pygame.key.get_mods()
            shift = mods & pygame.KMOD_SHIFT
            ctrl = mods & pygame.KMOD_CTRL

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

            # MUTE (CTRL = exclusive)
            if self.button_height - 20 <= local_y < self.button_height - 10:
                if ctrl:
                    tm.mute_exclusive(tid)
                else:
                    tm.set_mute(tid, not tm.is_muted(tid))
                self.event_bus.emit("track_mute", index, tm.is_muted(tid))
                self._emit_audible_state()
                return {"mute": index}

            # SOLO (SHIFT = exclusive)
            if local_y >= self.button_height - 10:
                if shift:
                    tm.solo_exclusive(tid)
                else:
                    tm.set_solo(tid, not tm.is_solo(tid))
                self.event_bus.emit("track_solo", index, tm.is_solo(tid))
                self._emit_audible_state()
                return {"solo": index}

            # SELECT TRACK
            try:
                tm.set_active_track(tid)
            except Exception:
                pass

            self.event_bus.emit("track_selected", index)
            self._emit_audible_state()

            # Fáza 4 – informujeme TrackControlManager o výbere stopy
            if self.track_control_manager is not None:
                try:
                    self.track_control_manager.select_track(index)
                except Exception:
                    pass

            return {"selected_track": index}

        return None
