import pygame
from typing import Optional, Tuple
from .track_control_manager import TrackControlManager


class TrackSelectorUI:
    """
    Horizontálny prepínač stôp.
    - zobrazuje farby stôp
    - umožňuje kliknutím vybrať aktívnu stopu
    - highlight aktívnej stopy
    - farby a viditeľnosť číta z TrackControlManager
    """

    def __init__(self, track_control_manager: TrackControlManager, width: int, height: int):
        pygame.font.init()

        self.track_control = track_control_manager
        self.width = width
        self.height = height

        self.track_count = 16
        self.button_width = max(1, width // self.track_count)
        self.button_height = height

        try:
            self.font = pygame.font.Font(None, 18)
        except Exception:
            self.font = None

        # Lokálny highlight (UIManager volá set_active_track)
        self.active_track = 0  # 0-based index

    # ---------------------------------------------------------
    # PUBLIC API (volané z UIManager event callbackov)
    # ---------------------------------------------------------
    def set_active_track(self, track_index: int):
        """UI reaguje na zmenu aktívnej stopy (0-based index)."""
        try:
            self.active_track = max(0, min(self.track_count - 1, int(track_index)))
        except Exception:
            self.active_track = 0

    def update_visibility(self, track_index: int, visible: bool):
        """Rezervované pre budúce rozšírenie."""
        pass

    def update_color(self, track_index: int, color_hex: str):
        """Farba sa berie priamo z TrackControlManager, netreba cache."""
        pass

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface, active_track=None):
        if active_track is not None:
            self.set_active_track(active_track)

        for i in range(self.track_count):
            rect = pygame.Rect(
                i * self.button_width,
                0,
                self.button_width,
                self.button_height
            )

            # Farba stopy z TrackControlManager
            try:
                color_hex = self.track_control.get_color(i)
                r = int(color_hex[1:3], 16)
                g = int(color_hex[3:5], 16)
                b = int(color_hex[5:7], 16)
                base_color = (r, g, b)
            except Exception:
                base_color = (120, 120, 120)

            pygame.draw.rect(surface, base_color, rect)

            # Aktívna stopa – biely rám
            if self.active_track == i:
                pygame.draw.rect(surface, (255, 255, 255), rect, 3)
            else:
                pygame.draw.rect(surface, (0, 0, 0), rect, 2)

            # Label (číslo stopy)
            if self.font is not None:
                label = f"{i+1}"
                text = self.font.render(label, True, (0, 0, 0))
                text_rect = text.get_rect(
                    center=(rect.x + self.button_width // 2, rect.y + self.button_height // 2)
                )
                surface.blit(text, text_rect)

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_click(self, pos):
        x, y = pos

        # Klik mimo panelu
        if not (0 <= x <= self.width and 0 <= y <= self.height):
            return

        index = int(x // self.button_width)
        index = max(0, min(self.track_count - 1, index))

        # Informujeme TrackControlManager (0-based index)
        try:
            self.track_control.select_track(index)
        except Exception:
            pass

        # Lokálny highlight
        self.active_track = index
