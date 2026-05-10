# =========================================================
# TrackSelectorUI v4.0.0
# Stabilný horizontálny prepínač MIDI stôp
# =========================================================

import pygame
from typing import Optional
from .track_control_manager import TrackControlManager


class TrackSelectorUI:
    """
    TrackSelectorUI (v4.0.0)
    ------------------------
    Horizontálny prepínač stôp.

    Vylepšenia v4:
        - okamžitý RGB lookup (bez HEX parsovania)
        - čistejšie kreslenie
        - bezpečné parsovanie indexov
        - hover-ready architektúra (pripravené pre v5)
        - drop‑in kompatibilita s UIManager
    """

    def __init__(self, track_control_manager: TrackControlManager, width: int, height: int):
        pygame.font.init()

        self.track_control = track_control_manager
        self.width = int(width)
        self.height = int(height)

        self.track_count = 16
        self.button_width = max(1, self.width // self.track_count)
        self.button_height = self.height

        try:
            self.font = pygame.font.Font(None, 18)
        except Exception:
            self.font = None

        # Aktívna stopa (UIManager volá set_active_track)
        self.active_track = 0

        # Cache pre čísla stôp (1–16)
        self._label_cache = {}
        if self.font:
            for i in range(self.track_count):
                label = f"{i + 1}"
                self._label_cache[i] = self.font.render(label, True, (0, 0, 0))

    # ---------------------------------------------------------
    # PUBLIC API (UIManager-safe)
    # ---------------------------------------------------------
    def set_active_track(self, track_index: int):
        """UI reaguje na zmenu aktívnej stopy (0-based index)."""
        try:
            self.active_track = max(0, min(self.track_count - 1, int(track_index)))
        except Exception:
            self.active_track = 0

    def update_visibility(self, track_index: int, visible: bool):
        return  # no-op

    def update_color(self, track_index: int, color_hex: str):
        return  # farby berieme z TrackControlManager

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface, active_track=None):
        if active_track is not None:
            self.set_active_track(active_track)

        get_color_rgb = self.track_control.get_color_rgb  # zrýchlený lookup

        for i in range(self.track_count):
            rect = pygame.Rect(
                i * self.button_width,
                0,
                self.button_width,
                self.button_height
            )

            # Farba stopy (RGB, real‑time safe)
            try:
                base_color = get_color_rgb(i)
            except Exception:
                base_color = (120, 120, 120)

            pygame.draw.rect(surface, base_color, rect)

            # Aktívna stopa – biely rám
            if self.active_track == i:
                pygame.draw.rect(surface, (255, 255, 255), rect, 2)
            else:
                pygame.draw.rect(surface, (0, 0, 0), rect, 1)

            # Label (číslo stopy)
            if self.font is not None:
                text = self._label_cache.get(i)
                if text:
                    text_rect = text.get_rect(
                        center=(rect.x + self.button_width // 2,
                                rect.y + self.button_height // 2)
                    )
                    surface.blit(text, text_rect)

    # ---------------------------------------------------------
    # EVENTS
    # ---------------------------------------------------------
    def handle_click(self, pos):
        x, y = pos

        # Klik mimo panelu
        if not (0 <= x < self.width and 0 <= y < self.height):
            return

        try:
            index = int(x // self.button_width)
        except Exception:
            return

        index = max(0, min(self.track_count - 1, index))

        # Informujeme TrackControlManager
        try:
            self.track_control.select_track(index)
        except Exception:
            pass

        # Lokálny highlight
        self.active_track = index
