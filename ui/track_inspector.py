import pygame
from typing import Optional, Tuple


class TrackInspector:
    """
    Track Inspector panel – interaktívny panel pre správu stôp.

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

        self.x = int(x)
        self.y = int(y)
        self.width = int(width)
        self.height = int(height)
        self.num_tracks = int(num_tracks)

        # layout
        self.header_height = 24
        self.row_height = 22
        self.padding = 6
        self.color_box_size = 14
        self.volume_bar_width = 80

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font = None

        # Lokálny stav pre eventy z UIManager
        self.active_track = 0  # 0-based index

    # ---------------------------------------------------------
    # PUBLIC API (volané z UIManager event callbackov)
    # ---------------------------------------------------------
    def set_active_track(self, track_index: int):
        """UI reaguje na zmenu aktívnej stopy (0-based index)."""
        try:
            self.active_track = max(0, int(track_index))
        except Exception:
            self.active_track = 0

    def update_visibility(self, track_index: int, visible: bool):
        """UI si viditeľnosť necache-uje – no-op."""
        return

    def update_color(self, track_index: int, color_hex: str):
        """UI si farby necache-uje – no-op."""
        return

    # ---------------------------------------------------------
    # HELPERS
    # ---------------------------------------------------------
    @staticmethod
    def _hex_to_rgb(h: str) -> Tuple[int, int, int]:
        h = h.lstrip("#")
        return (
            int(h[0:2], 16),
            int(h[2:4], 16),
            int(h[4:6], 16),
        )

    def _get_track_color(self, track_id: int) -> Tuple[int, int, int]:
        # track_id je 1-based
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
        # track_id je 1-based
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

        # Panel bounds
        if not (self.x <= mx <= self.x + self.width and
                self.y <= my <= self.y + self.height):
            return

        bar_x_base = self.x + self.width - self.padding - self.volume_bar_width

        for track_id in range(1, self.num_tracks + 1):
            row_top = self.y + self.header_height + (track_id - 1) * self.row_height
            row_rect = pygame.Rect(self.x, row_top, self.width, self.row_height)

            if not row_rect.collidepoint(mx, my):
                continue

            # 1) klik na oko (visibility)
            vis_rect = pygame.Rect(
                row_rect.x + self.padding,
                row_rect.y + (self.row_height - 10) // 2,
                10,
                10,
            )
            if vis_rect.collidepoint(mx, my):
                if self.track_control is not None:
                    try:
                        self.track_control.toggle_visibility(track_id - 1)
                    except Exception:
                        pass
                return

            # 2) klik na volume bar
            bar_rect = pygame.Rect(
                bar_x_base,
                row_rect.y + 4,
                self.volume_bar_width,
                self.row_height - 8,
            )
            if bar_rect.collidepoint(mx, my):
                rel = (mx - bar_x_base) / self.volume_bar_width
                rel = max(0.0, min(1.0, rel))
                try:
                    self.track_manager.set_volume(track_id, rel)
                except Exception:
                    pass
                return

            # 3) klik na riadok → nastaviť aktívnu stopu
            if self.track_control is not None:
                try:
                    self.track_control.select_track(track_id - 1)
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
        bar_x_base = self.x + self.width - self.padding - self.volume_bar_width

        for track_id in range(1, self.num_tracks + 1):
            row_top = self.y + self.header_height + (track_id - 1) * self.row_height
            if row_top + self.row_height > self.y + self.height:
                break

            row_rect = pygame.Rect(self.x + 1, row_top, self.width - 2, self.row_height)

            bg_color = (40, 40, 60) if track_id == active_track_id else (28, 28, 28)
            pygame.draw.rect(surface, bg_color, row_rect)

            # visibility
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

            # color box
            base_color = self._get_track_color(track_id)
            color_rect = pygame.Rect(
                vis_rect.right + 6,
                row_rect.y + (self.row_height - self.color_box_size) // 2,
                self.color_box_size,
                self.color_box_size,
            )
            pygame.draw.rect(surface, base_color, color_rect)
            pygame.draw.rect(surface, (0, 0, 0), color_rect, 1)

            # name
            if self.font is not None:
                name = self._get_track_name(track_id)
                name_surf = self.font.render(
                    name,
                    True,
                    (230, 230, 230) if visible else (140, 140, 140),
                )
                surface.blit(name_surf, (color_rect.right + 6, row_rect.y + 3))

            # volume bar
            vol = self._get_track_volume(track_id)
            if vol is not None:
                bar_y = row_rect.y + 4
                bar_h = self.row_height - 8

                pygame.draw.rect(
                    surface,
                    (35, 35, 35),
                    (bar_x_base, bar_y, self.volume_bar_width, bar_h),
                )
                pygame.draw.rect(
                    surface,
                    (0, 0, 0),
                    (bar_x_base, bar_y, self.volume_bar_width, bar_h),
                    1,
                )

                fill_w = int(self.volume_bar_width * vol)
                pygame.draw.rect(
                    surface,
                    (120, 200, 120),
                    (bar_x_base + 1, bar_y + 1, max(0, fill_w - 2), bar_h - 2),
                )

        pygame.draw.rect(surface, (90, 90, 90), panel_rect, 1)
