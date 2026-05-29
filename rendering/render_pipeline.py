# =========================================================
# render_pipeline.py v4.3.0
# Modular rendering orchestrator for UI components
# =========================================================

from __future__ import annotations
from typing import List, Optional, Any
import pygame


class RenderPipeline:
    """
    RenderPipeline (v4.3.0)
    -----------------------
    Lightweight orchestrator for rendering UI components
    in a deterministic, real-time safe order.

    Features:
        - modular render stages
        - deterministic ordering
        - real-time safe (no exceptions)
        - __slots__ for ultra-low latency
        - zero-allocation hot path
        - ready for v5 (AI layout, adaptive rendering)
    """

    __slots__ = (
        "enabled",
        "_stages",
        "_sorted",
    )

    def __init__(self, enabled: bool = True):
        self.enabled = bool(enabled)
        self._stages: List[tuple[int, Any]] = []   # (priority, component)
        self._sorted = False

    # ---------------------------------------------------------
    # STAGE MANAGEMENT
    # ---------------------------------------------------------
    def add_stage(self, priority: int, component: Any) -> None:
        """
        Add a render stage with a given priority.
        Lower priority = drawn earlier (background).
        """
        try:
            self._stages.append((int(priority), component))
            self._sorted = False
        except Exception:
            pass

    def clear(self) -> None:
        """Remove all stages."""
        try:
            self._stages.clear()
            self._sorted = False
        except Exception:
            pass

    # ---------------------------------------------------------
    # SORTING
    # ---------------------------------------------------------
    def _ensure_sorted(self) -> None:
        """Sort stages by priority if needed."""
        if self._sorted:
            return
        try:
            self._stages.sort(key=lambda x: x[0])
        except Exception:
            pass
        self._sorted = True

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface) -> None:
        """
        Render all registered components in order.
        Each component must implement draw(surface).
        """
        if not self.enabled or surface is None:
            return

        self._ensure_sorted()

        try:
            for _, comp in self._stages:
                try:
                    draw_fn = getattr(comp, "draw", None)
                    if callable(draw_fn):
                        draw_fn(surface)
                except Exception:
                    # Never break real-time rendering
                    pass
        except Exception:
            pass

    # ---------------------------------------------------------
    # TOGGLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Toggle pipeline state."""
        self.enabled = not self.enabled
        return self.enabled
