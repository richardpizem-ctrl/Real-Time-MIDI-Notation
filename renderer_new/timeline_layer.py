# =========================================================
# TimelineLayer v2.0.0
# Stabilná vrstva pre kreslenie timeline (grid + markers + playhead)
# =========================================================

import pygame
from typing import Optional
from ..timeline_controller import TimelineController
from .layers import BaseLayer


class TimelineLayer(BaseLayer):
    """
    TimelineLayer (v2.0.0)
    ----------------------
    - Vrstva pre kreslenie timeline
    - Nepoužíva vlastnú logiku, iba deleguje kreslenie
      na TimelineController
    - Real‑time safe
    - Pripravené na v3 (AI/TIMELINE)
    """

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
        if self.controller is None or surface is None:
            return

        try:
            # Grid
            self.controller.draw_grid(surface)

            # Markers
            self.controller.draw_markers(surface)

            # Playhead
            self.controller.draw_playhead(surface)

        except Exception:
            # Timeline musí byť real‑time safe
            pass
