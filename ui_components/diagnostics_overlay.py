# =========================================================
# diagnostics_overlay.py v4.3.0
# Ultra-light FPS / performance diagnostics overlay (pygame)
# =========================================================

from __future__ import annotations

import pygame
from typing import Optional, Tuple


class DiagnosticsOverlay:
    """
    DiagnosticsOverlay (v4.3.0)
    ---------------------------
    Lightweight on-screen diagnostics panel.

    Features:
        - FPS display
        - optional frame time (ms)
        - optional external PerformanceMonitor hook
        - real-time safe
        - no exceptions
        - __slots__ for low latency
    """

    __slots__ = (
        "enabled",
        "font",
        "bg_color",
        "text_color",
        "border_color",
        "padding",
        "position",
        "perf_monitor",
    )

    def __init__(
        self,
        enabled: bool = True,
        position: str = "top_left",
        bg_color: Tuple[int, int, int] = (0, 0, 0),
        text_color: Tuple[int, int, int] = (0, 255, 0),
        border_color: Tuple[int, int, int] = (60, 60, 60),
        perf_monitor: Optional[object] = None,
    ) -> None:
        """
        :param enabled: overlay visibility
        :param position: 'top_left', 'top_right', 'bottom_left', 'bottom_right'
        :param bg_color: background color
        :param text_color: text color
        :param border_color: border color
        :param perf_monitor: optional PerformanceMonitor instance
                             (must expose get_fps() / get_frame_time_ms() if used)
        """
        self.enabled = bool(enabled)
        self.position = position
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_color = border_color
        self.padding = 6
        self.perf_monitor = perf_monitor

        pygame.font.init()
        try:
            self.font = pygame.font.SysFont("Consolas", 14)
        except Exception:
            self.font = pygame.font.Font(None, 14)

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Toggle overlay visibility and return new state."""
        self.enabled = not self.enabled
        return self.enabled

    def set_perf_monitor(self, monitor: object) -> None:
        """Attach or replace external PerformanceMonitor."""
        self.perf_monitor = monitor

    # ---------------------------------------------------------
    # DATA GATHERING
    # ---------------------------------------------------------
    def _get_metrics(self, clock: Optional[pygame.time.Clock]) -> Tuple[str, Optional[str]]:
        """
        Returns (fps_text, frame_time_text_or_None).
        Uses either external perf_monitor or pygame Clock.
        """
        fps_text = "FPS: ?"
        ft_text: Optional[str] = None

        # External PerformanceMonitor has priority
        pm = self.perf_monitor
        if pm is not None:
            try:
                fps = getattr(pm, "get_fps", None)
                ft = getattr(pm, "get_frame_time_ms", None)

                if callable(fps):
                    v = fps()
                    fps_text = f"FPS: {v:.1f}" if isinstance(v, (int, float)) else f"FPS: {v}"

                if callable(ft):
                    v = ft()
                    ft_text = f"{v:.2f} ms" if isinstance(v, (int, float)) else str(v)

                return fps_text, ft_text
            except Exception:
                # fall back to clock
                pass

        if clock is not None:
            try:
                fps_val = clock.get_fps()
                fps_text = f"FPS: {fps_val:.1f}"
            except Exception:
                fps_text = "FPS: ?"

        return fps_text, ft_text

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface, clock: Optional[pygame.time.Clock] = None) -> None:
        """
        Draw diagnostics overlay onto given surface.

        :param surface: main pygame surface
        :param clock: optional pygame.time.Clock for FPS
        """
        if not self.enabled or surface is None:
            return

        try:
            fps_text, ft_text = self._get_metrics(clock)

            lines = [fps_text]
            if ft_text is not None:
                lines.append(f"Frame: {ft_text}")

            # Render text surfaces
            text_surfaces = [self.font.render(line, True, self.text_color) for line in lines]

            width = max(ts.get_width() for ts in text_surfaces) + self.padding * 2
            height = sum(ts.get_height() for ts in text_surfaces) + self.padding * 2

            sw, sh = surface.get_size()
            x, y = self._compute_position(sw, sh, width, height)

            rect = pygame.Rect(x, y, width, height)

            pygame.draw.rect(surface, self.bg_color, rect)
            pygame.draw.rect(surface, self.border_color, rect, 1)

            cy = y + self.padding
            for ts in text_surfaces:
                surface.blit(ts, (x + self.padding, cy))
                cy += ts.get_height()

        except Exception:
            # overlay must never break rendering
            return

    # ---------------------------------------------------------
    # POSITIONING
    # ---------------------------------------------------------
    def _compute_position(self, sw: int, sh: int, w: int, h: int) -> Tuple[int, int]:
        """Compute overlay position based on configured corner."""
        pos = self.position

        if pos == "top_right":
            return sw - w - 8, 8
        if pos == "bottom_left":
            return 8, sh - h - 8
        if pos == "bottom_right":
            return sw - w - 8, sh - h - 8

        # default: top_left
        return 8, 8
