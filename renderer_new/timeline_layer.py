# =========================================================
# TimelineLayer v4.3.0
# Optimalizovaná vrstva pre kreslenie timeline (grid + markers + playhead)
# - real‑time safe
# - mikrooptimalizácie
# - diagnostické fallbacky
# - prepojené s TimelineController v4.3.0
# =========================================================

import pygame
from typing import Optional
from ..timeline_controller import TimelineController
from .layers import BaseLayer


class TimelineLayer(BaseLayer):
    """
    TimelineLayer (v4.3.0)
    ----------------------
    - Vrstva pre kreslenie timeline
    - Deleguje kreslenie na TimelineController
    - Real‑time safe
    - Partial redraw friendly
    - Optimalizované pre renderer_new
    """

    __slots__ = ("controller",)

    def __init__(self, controller: TimelineController, z_index: int = 0):
        super().__init__(z_index=z_index, visible=True)
        self.controller = controller

    def draw(self, surface: pygame.Surface):
        """
        Kreslí timeline cez controller.
        Poradie:
            1. Grid
            2. Markers
            3. Playhead
        """
        ctrl = self.controller
        if ctrl is None or surface is None:
            return

        try:
            # Grid
            ctrl.draw_grid(surface)

            # Markers
            ctrl.draw_markers(surface)

            # Playhead
            ctrl.draw_playhead(surface)

        except Exception:
            # Timeline musí byť real‑time safe
            pass
