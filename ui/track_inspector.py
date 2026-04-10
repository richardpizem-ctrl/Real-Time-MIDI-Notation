import pygame
from typing import Optional, Tuple


class TrackInspector:
    """
    Track Inspector panel – teraz už aj s interakciou.

    - číta stav z track_manager a track_control
    - umožňuje kliknúť na:
        • riadok → nastaviť aktívnu stopu
        • oko → toggle visibility
        • volume bar → zmeniť hlasitosť
    """

    def __init__(
        self,
        track_manager,
        track_control=None,
        x: int = 10,
        y: int = 10,
        width: int = 260,
        height: int = 400,
        num_tracks: int = 16,
    ):
        self.track_manager = track_manager
        self.track_control = track_control

        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.num_tracks = num_tracks

        # layout
        self.header_height = 24
        self.row_height = 22
        self.padding = 6
        self.color_box_size = 14
        self.volume_bar_width = 80

        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    def _hex_to_rgb(self, h: str) -> Tuple[int, int, int]:
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def _get_track_color(self, track_id: int) -> Tuple[int, int, int]:
        if self.track_control is not None:
            try:
                hex_color = self.track_control.get_color(track_id - 1)
                return self._hex_to_rgb(hex_color)
            except Exception:
                pass

        try:
            return self.track_manager.get_color(track_id)
        except Exception:
            return (120, 180, 220)

    def _get_track_name(self, track_id: int) -> str:
        try:
            name = self.track_manager.get_name(track_id)
            if isinstance(name, str) and name.strip():
                return name
        except Exception:
            pass
        return f"Track {track_id}"

    def _get_track_visible(self, track_id: int) -> bool:
        if self.track_control is not None:
            try:
                return bool(self.track_control.is_visible(track_id - 1))
            except Exception:
                pass

        try:
            return bool(self.track_manager.is_visible(track_id))
        except Exception:
            return True

    def _get_active_track_id(self) -> Optional[int]:
        try:
            if self.track_control is not None:
                return int(self.track_control.get_active_track()) + 1
            return int(self.track_manager.get_active_track())
        except Exception:
            return None

    def _get_track_volume(self, track_id: int) -> Optional[float]:
        try:
            v = float(self.track_manager.get_volume(track_id))
            return max(0.0, min(1.0, v))
        except Exception:
            return None

    # ---------------------------------------------------------
    # INTERAKCIA
    # ---------------------------------------------------------
    def handle_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return

        mx, my = event.pos

        # klik mimo panelu
        if not (self.x <= mx <= self.x + self.width and
                self.y <= my <= self.y + self.height):
            return

        # klik na riadok
        for track_id in range(1, self.num_tracks + 1):
            row_top = self.y + self.header_height + (track_id - 1) * self.row_height
            row_rect = pygame.Rect(self.x, row_top, self.width, self.row_height)

            if row_rect.collidepoint(mx, my):

                # 1) klik na oko (visibility)
                vis_rect = pygame.Rect(
                    row_rect.x + self.padding,
                    row_rect.y + (self.row_height - 10) // 2,
                    10,
                    10,
                )
                if vis_rect.collidepoint(mx, my):
                    try:
                        current = self.track_control.is_visible(track_id - 1)
                        self.track_control.set_visible(track_id - 1, not current)
                    except Exception:
                        pass
                    return

                # 2) klik na volume bar
                bar_x = self.x + self.width - self.padding - self.volume_bar_width
                bar_y = row_rect.y + 4
                bar_rect = pygame.Rect(bar_x, bar_y, self.volume_bar_width, self.row_height - 8)

                if bar_rect.collidepoint(mx, my):
                    rel = (mx - bar_x) / self.volume_bar_width
                    rel = max(0.0, min(1.0, rel))
                    try:
                        self.track_manager.set_volume(track_id, rel)
                    except Exception:
                        pass
                    return

                # 3) klik na riadok → nastaviť aktívnu stopu
                try:
                    self.track_control.set_active_track(track_id - 1)
                except Exception:
                    pass

                return

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        if surface is None:
            return

        panel_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (18, 18, 18), panel_rect)
        pygame.draw.rect(surface, (70, 70, 70), panel_rect, 1)

        if self.font is not None:
            header_text = self.font.render("TRACK INSPECTOR", True, (230, 230, 230))
            surface.blit(header_text, (self.x + self.padding, self.y + 3))

        pygame.draw.line(
            surface,
            (70, 70, 70),
            (self.x, self.y + self.header_height),
            (self.x + self.width, self.y + self.header_height),
            1,
        )

        active_track_id = self._get_active_track_id()

        for track_id in range(1, self.num_tracks + 1):
            row_top = self.y + self.header_height + (track_id - 1) * self.row_height
            if row_top + self.row_height > self.y + self.height:
                break

            row_rect = pygame.Rect(self.x + 1, row_top, self.width - 2, self.row_height)

            bg_color = (40, 40, 60) if track_id == active_track_id else (28, 28, 28)
            pygame.draw.rect(surface, bg_color, row_rect)

            visible = self._get_track_visible(track_id)
            vis_color = (140, 220, 140) if visible else (120, 120, 120)
            vis_rect = pygame.Rect(
                row_rect.x + self.padding,
                row_rect.y + (self.row_height - 10) // 2,
                10,
                10,
            )
            pygame.draw.rect(surface, vis_color, vis_rect)
            pygame.draw.rect(surface, (0, 0, 0), vis_rect, 1)

            base_color = self._get_track_color(track_id)
            color_rect = pygame.Rect(
                vis_rect.right + 6,
                row_rect.y + (self.row_height - self.color_box_size) // 2,
                self.color_box_size,
                self.color_box_size,
            )
            pygame.draw.rect(surface, base_color, color_rect)
            pygame.draw.rect(surface, (0, 0, 0), color_rect, 1)

            if self.font is not None:
                name = self._get_track_name(track_id)
                name_surf = self.font.render(
                    name,
                    True,
                    (230, 230, 230) if visible else (140, 140, 140),
                )
                surface.blit(name_surf, (color_rect.right + 6, row_rect.y + 3))

            vol = self._get_track_volume(track_id)
            if vol is not None:
                bar_x = self.x + self.width - self.padding - self.volume_bar_width
                bar_y = row_rect.y + 4
                bar_h = self.row_height - 8

                pygame.draw.rect(surface, (35, 35, 35), (bar_x, bar_y, self.volume_bar_width, bar_h))
                pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, self.volume_bar_width, bar_h), 1)

                fill_w = int(self.volume_bar_width * vol)
                pygame.draw.rect(
                    surface,
                    (120, 200, 120),
                    (bar_x + 1, bar_y + 1, max(0, fill_w - 2), bar_h - 2),
                )

        pygame.draw.rect(surface, (90, 90, 90), panel_rect, 1)
