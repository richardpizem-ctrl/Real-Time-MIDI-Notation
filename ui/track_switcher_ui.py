import pygame
import math
from .track_control_manager import TrackControlManager


class TrackSwitcherUI:
    TRACK_COUNT = 16
    METER_HEIGHT = 20
    VOLUME_HEIGHT = 30
    NAME_HEIGHT = 20
    SHADOW_HEIGHT = 10
    GLOW_LAYERS = 6

    COLOR_METER_BG = (20, 20, 20)
    COLOR_VOLUME_BG = (15, 15, 25)
    COLOR_PAN_BG = (20, 20, 20)
    COLOR_METER = (0, 255, 0)
    COLOR_PEAK = (255, 255, 255)
    COLOR_VOLUME = (180, 180, 255)
    COLOR_NAME_SEPARATOR = (0, 0, 0, 30)
    COLOR_SEPARATOR = (0, 0, 0, 20)
    COLOR_DIVIDER = (0, 0, 0, 25)
    COLOR_SHADOW = (0, 0, 0)
    COLOR_OUTER_GLOW = (255, 255, 255)
    COLOR_TOOLTIP_BG = (240, 240, 240)
    COLOR_TOOLTIP_BORDER = (0, 0, 0)

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

        self.track_count = self.TRACK_COUNT
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
    def _draw_gradient(self, surface, rect, base_color):
        r, g, b = base_color
        height = rect.height
        for y in range(height):
            factor = y / height
            shade = (
                int(r * (1 - factor * 0.3)),
                int(g * (1 - factor * 0.3)),
                int(b * (1 - factor * 0.3)),
            )
            pygame.draw.line(surface, shade, (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))

    def _draw_inner_highlight(self, surface, rect):
        highlight_height = 6
        for i in range(highlight_height):
            alpha = int(60 * (1 - i / highlight_height))
            shade = (255, 255, 255, alpha)
            pygame.draw.line(
                surface,
                shade,
                (rect.x + 2, rect.y + 2 + i),
                (rect.x + rect.width - 2, rect.y + 2 + i),
                1,
            )

    def _draw_separator(self, surface, rect, y_offset):
        pygame.draw.line(
            surface,
            self.COLOR_SEPARATOR,
            (rect.x + 2, rect.y + y_offset),
            (rect.x + rect.width - 2, rect.y + y_offset),
            1,
        )

    def _draw_vertical_divider(self, surface, rect):
        pygame.draw.line(
            surface,
            self.COLOR_DIVIDER,
            (rect.right, rect.y + 4),
            (rect.right, rect.y + rect.height - 4),
            1,
        )

    def _draw_shadow(self, surface, rect):
        for i in range(self.SHADOW_HEIGHT):
            alpha = int(45 * (1 - i / self.SHADOW_HEIGHT))
            shade = (*self.COLOR_SHADOW[:3], alpha)
            pygame.draw.line(
                surface,
                shade,
                (rect.x - 2, rect.y + rect.height + i),
                (rect.x + rect.width + 2, rect.y + rect.height + i),
                1,
            )

    def _draw_outer_glow(self, surface, rect, intensity=60):
        for i in range(self.GLOW_LAYERS):
            alpha = int(intensity * (1 - i / self.GLOW_LAYERS))
            color = (*self.COLOR_OUTER_GLOW[:3], alpha)
            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(
                    rect.x - i,
                    rect.y - i,
                    rect.width + i * 2,
                    rect.height + i * 2,
                ),
                width=2,
                border_radius=6 + i,
            )

    def _draw_meter_background(self, surface, rect):
        bg_rect = pygame.Rect(rect.x + 4, rect.y + 2, self.button_width - 8, self.METER_HEIGHT)
        pygame.draw.rect(surface, self.COLOR_METER_BG, bg_rect, border_radius=4)

    def _draw_meter(self, surface, rect, level):
        if level <= 0:
            return
        meter_height = int(level * self.METER_HEIGHT)
        meter_rect = pygame.Rect(
            rect.x + 4,
            rect.y + 2 + (self.METER_HEIGHT - meter_height),
            self.button_width - 8,
            meter_height,
        )
        pygame.draw.rect(surface, self.COLOR_METER, meter_rect, border_radius=3)

    def _draw_peak(self, surface, rect, peak):
        if peak <= 0:
            return
        peak_y = rect.y + 2 + int((1 - peak) * self.METER_HEIGHT)
        peak_rect = pygame.Rect(rect.x + 4, peak_y, self.button_width - 8, 2)
        pygame.draw.rect(surface, self.COLOR_PEAK, peak_rect, border_radius=2)

    def _draw_volume_background(self, surface, rect):
        frame_rect = pygame.Rect(
            rect.x + 6,
            rect.y + self.button_height - 55,
            self.button_width - 12,
            self.VOLUME_HEIGHT,
        )
        pygame.draw.rect(surface, self.COLOR_VOLUME_BG, frame_rect, border_radius=4)

    def _draw_volume(self, surface, rect, vol):
        try:
            vol = max(0.0, min(1.0, float(vol)))
        except Exception:
            vol = 0.0

        vol_h = int(vol * self.VOLUME_HEIGHT)
        vol_rect = pygame.Rect(
            rect.x + 6,
            rect.y + self.button_height - 55 + (self.VOLUME_HEIGHT - vol_h),
            self.button_width - 12,
            vol_h,
        )
        pygame.draw.rect(surface, self.COLOR_VOLUME, vol_rect, border_radius=3)

        if self.small_font:
            txt = self.small_font.render("V", True, (0, 0, 0))
            surface.blit(txt, (rect.x + 2, rect.y + self.button_height - 60))

    def _draw_pan_background(self, surface, rect):
        pan_x = rect.x + self.button_width // 2
        pan_y = rect.y + self.button_height - 70
        bg_rect = pygame.Rect(pan_x - 10, pan_y - 10, 20, 20)
        pygame.draw.rect(surface, self.COLOR_PAN_BG, bg_rect, border_radius=6)

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
        if active:
            glow_rect = rect.inflate(4, 4)
            pygame.draw.rect(surface, (255, 255, 255, 40), glow_rect, border_radius=6)
        pygame.draw.rect(surface, color_on if active else color_off, rect, border_radius=6)
        if self.small_font:
            txt = self.small_font.render(label, True, (0, 0, 0))
            surface.blit(txt, (rect.x + 2, rect.y + 1))

    def _draw_name_separator(self, surface, rect):
        y = rect.y + self.NAME_HEIGHT
        pygame.draw.line(
            surface,
            self.COLOR_NAME_SEPARATOR,
            (rect.x + 4, y),
            (rect.x + rect.width - 4, y),
            1,
        )

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface, active_track=None):
        tm = self.event_bus.track_manager
        any_solo = self._any_solo()

        self.update_peak_hold()

        if self.track_control_manager is not None:
            active_tid = self.track_control_manager.get_active_track() + 1
        else:
            active_tid = active_track

        mx, my = pygame.mouse.get_pos()
        tooltip_text = None
        tooltip_pos = None

        for i in range(self.track_count):
            tid = i + 1

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

            # GRADIENT + VNÚTORNÝ LESK
            self._draw_gradient(surface, rect, base_color)
            self._draw_inner_highlight(surface, rect)

            # OVERLAY
            try:
                if tm.is_muted(tid):
                    overlay = (120, 120, 120)
                elif any_solo:
                    overlay = (255, 255, 120) if tm.is_solo(tid) else (80, 80, 80)
                else:
                    overlay = (255, 255, 120) if tm.is_solo(tid) else base_color
            except Exception:
                overlay = base_color

            pygame.draw.rect(surface, overlay, rect, border_radius=6)
            pygame.draw.rect(surface, (0, 0, 0), rect, 2, border_radius=6)

            # OUTER GLOW – HOVER
            if rect.collidepoint(mx, my):
                self._draw_outer_glow(surface, rect, intensity=40)

            # OUTER GLOW – ACTIVE TRACK + jemný biely rámik
            if active_tid == tid:
                self._draw_outer_glow(surface, rect, intensity=70)
                pygame.draw.rect(surface, (255, 255, 255), rect.inflate(-2, -2), 1, border_radius=6)

            # METER BACKGROUND + METER + PEAK
            activity = tm.get_activity(tid)
            self._draw_meter_background(surface, rect)
            self._draw_meter(surface, rect, activity)
            self._draw_peak(surface, rect, self.peak_hold[i])

            # PAN BACKGROUND + PAN
            pan_val = tm.get_pan(tid)
            self._draw_pan_background(surface, rect)
            self._draw_pan(surface, rect, pan_val)
            self._draw_separator(surface, rect, self.button_height - 65)

            # VOLUME BACKGROUND + VOLUME
            volume = tm.get_volume(tid)
            self._draw_volume_background(surface, rect)
            self._draw_volume(surface, rect, volume)
            self._draw_separator(surface, rect, self.button_height - 25)

            # RECORD ARM
            rec_rect = pygame.Rect(rect.x + 4, rect.y + self.button_height - 85, self.button_width - 8, 10)
            rec_active = tm.is_record_armed(tid)
            self._draw_button(surface, rec_rect, rec_active, (255, 0, 0), (80, 0, 0), "R")
            self._draw_separator(surface, rect, self.button_height - 75)

            # MUTE
            mute_rect = pygame.Rect(rect.x + 4, rect.y + self.button_height - 20, self.button_width - 8, 10)
            mute_active = tm.is_muted(tid)
            self._draw_button(surface, mute_rect, mute_active, (255, 80, 80), (100, 40, 40), "M")
            self._draw_separator(surface, rect, self.button_height - 10)

            # SOLO
            solo_rect = pygame.Rect(rect.x + 4, rect.y + self.button_height - 10, self.button_width - 8, 10)
            solo_active = tm.is_solo(tid)
            self._draw_button(surface, solo_rect, solo_active, (255, 255, 80), (100, 100, 40), "S")

            # TOOLTIP DETEKCIA
            if rect.collidepoint(mx, my):
                local_y = my - rect.y
                if self.button_height - 85 <= local_y < self.button_height - 75:
                    tooltip_text = "Record"
                elif self.button_height - 75 <= local_y < self.button_height - 65:
                    tooltip_text = "Pan"
                elif self.button_height - 55 <= local_y < self.button_height - 25:
                    tooltip_text = "Volume"
                elif self.button_height - 20 <= local_y < self.button_height - 10:
                    tooltip_text = "Mute"
                elif local_y >= self.button_height - 10:
                    tooltip_text = "Solo"
                tooltip_pos = (mx + 8, my - 18)

            # NAME
            try:
                name = tm.get_name(tid)
            except Exception:
                name = f"Track {tid}"

            name_color = (255, 255, 255) if active_tid == tid else (0, 0, 0)

            if self.font:
                text_surface = self.font.render(name, True, name_color)
                text_rect = text_surface.get_rect(center=(rect.x + self.button_width // 2, rect.y + 12))
                surface.blit(text_surface, text_rect)

            # NAME SEPARATOR
            self._draw_name_separator(surface, rect)

            # VERTIKÁLNY DIVIDER (okrem posledného tracku)
            if i < self.track_count - 1:
                self._draw_vertical_divider(surface, rect)

            # TIEŇ
            self._draw_shadow(surface, rect)

        # TOOLTIP RENDER
        if tooltip_text and self.small_font:
            tip_surf = self.small_font.render(tooltip_text, True, (0, 0, 0))
            bg_rect = tip_surf.get_rect(topleft=tooltip_pos).inflate(6, 4)
            pygame.draw.rect(surface, self.COLOR_TOOLTIP_BG, bg_rect, border_radius=4)
            pygame.draw.rect(surface, self.COLOR_TOOLTIP_BORDER, bg_rect, 1, border_radius=4)
            surface.blit(tip_surf, (bg_rect.x + 3, bg_rect.y + 2))

    # ---------------------------------------------------------
    # PUBLIC API PRE UIManager (ZJEDNOTENÉ
