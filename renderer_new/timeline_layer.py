"""
timeline_layer.py
FÁZA 4 – Timeline Layer pre nový LayerManager

Účel:
    - Kreslí timeline (grid, markers, playhead)
    - Používa TimelineController ako zdroj dát
    - Integruje sa do LayerManager v graphic_renderer.py
"""

import pygame
from typing import Optional
from ..timeline_controller import TimelineController
from .renderer_layers import BaseLayer


class TimelineLayer(BaseLayer):
    """
    TimelineLayer – vrstva pre kreslenie timeline.
    Nepoužíva žiadnu vlastnú logiku, iba deleguje kreslenie
    na TimelineController.
    """

    def __init__(self, controller: TimelineController):
        super().__init__("timeline", visible=True)
        self.controller = controller

    def draw(self, surface: pygame.Surface, context=None):
        """
        Kreslí timeline cez controller.
        Poradie:
            1. Grid
            2. Markers
            3. Playhead
        """
        if self.controller is None:
            return

        # 🔒 Odporúčaná ochrana (pridané)
        if surface is None:
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
