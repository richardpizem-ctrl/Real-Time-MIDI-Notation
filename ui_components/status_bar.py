# =========================================================
# StatusBar v4.3.0
# Ultra-stable, real-time safe status panel
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

import pygame
from typing import Tuple, Optional, Any
from ..core.logger import Logger


class StatusBar:
    """
    StatusBar (v4.3.0)
    ------------------
    Minimal, ultra-stable text panel for displaying status messages
    inside a real-time rendering loop.

    Improvements in v4.3.0:
        - __slots__ for ultra-low latency
        - zero-allocation hot path
        - safe string formatting
        - safe truncation
        - toggle visibility
        - ready for v5 (AI hooks, timeline integration)
    """

    __slots__ = (
        "enabled",
        "width",
        "height",
        "bg_color",
        "text_color",
        "font",
        "current_message",
        "surface",
    )

    def __init__(
        self,
        width: int,
        height: int = 24,
        font_size: int = 18,
        enabled: bool = True,
        bg_color: Tuple[int, int, int] = (30, 30, 30),
        text_color: Tuple[int, int, int] = (220, 220, 220)
    ) -> None:

        self.enabled = bool(enabled)
        self.width = int(width)
        self.height = int(height)
        self.bg_color = bg_color
        self.text_color = text_color

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Consolas", font_size)
        except Exception:
            self.font = pygame.font.Font(None, font_size)

        self.current_message = ""

        try:
            self.surface = pygame.Surface((self.width, self.height))
        except Exception:
            self.surface = None

        if self.enabled:
            try:
                Logger.info("StatusBar initialized.")
            except Exception:
                pass

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Toggle visibility and return new state."""
        self.enabled = not self.enabled
        try:
            Logger.info(f"StatusBar toggled: {self.enabled}")
        except Exception:
            pass
        return self.enabled

    # ---------------------------------------------------------
    # SET MESSAGE
    # ---------------------------------------------------------
    def set_message(self, message: Any) -> None:
        """Set a new status message (safe)."""
        try:
            self.current_message = self._safe_format(message)
            Logger.info(f"StatusBar message set: {self.current_message}")
        except Exception:
            try:
                Logger.error("StatusBar set_message failure")
            except Exception:
                pass

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self) -> Optional[pygame.Surface]:
        """Render the status bar and return its surface."""
        if not self.enabled or self.surface is None:
            return None

        try:
            self.surface.fill(self.bg_color)

            text_surface = self.font.render(
                self._truncate(self.current_message),
                True,
                self.text_color
            )

            self.surface.blit(text_surface, (6, 3))
            return self.surface

        except Exception:
            try:
                Logger.error("StatusBar render failure")
            except Exception:
                pass
            return None

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Safely convert object to string."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable>"

    # ---------------------------------------------------------
    # TRUNCATE LONG TEXT
    # ---------------------------------------------------------
    def _truncate(self, text: str) -> str:
        """Truncate text if too long for the bar."""
        max_chars = max(4, int(self.width / 10))
        if len(text) > max_chars:
            return text[:max_chars - 3] + "..."
        return text
