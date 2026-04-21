"""
renderer_layers.py
Layer system for the new Graphic Notation Renderer.

This module defines:
- BaseLayer: abstract layer interface
- Concrete layers: NotesLayer, GridLayer, PlayheadLayer, MarkerLayer
- LayerManager: manages ordering, visibility and drawing
"""

from abc import ABC, abstractmethod
from typing import List, Optional
import pygame


# ------------------------------------------------------------
# BASE LAYER
# ------------------------------------------------------------

class BaseLayer(ABC):
    """Abstract base class for all renderer layers."""

    def __init__(self, name: str, visible: bool = True):
        self.name = name
        self.visible = visible

    @abstractmethod
    def draw(self, surface: pygame.Surface, context):
        """Draw the layer using the provided rendering context."""
        pass

    def set_visible(self, state: bool):
        self.visible = state


# ------------------------------------------------------------
# EXAMPLE LAYERS
# ------------------------------------------------------------

class GridLayer(BaseLayer):
    """Draws timeline/grid background."""

    def __init__(self):
        super().__init__("grid")

    def draw(self, surface: pygame.Surface, context):
        grid = context.timeline_grid
        grid.draw(surface)


class NotesLayer(BaseLayer):
    """Draws MIDI notes."""

    def __init__(self):
        super().__init__("notes")

    def draw(self, surface: pygame.Surface, context):
        renderer = context.note_renderer
        renderer.draw(surface)


class PlayheadLayer(BaseLayer):
    """Draws the playhead line."""

    def __init__(self):
        super().__init__("playhead")

    def draw(self, surface: pygame.Surface, context):
        playhead = context.playhead
        playhead.draw(surface)


class MarkerLayer(BaseLayer):
    """Draws timeline markers."""

    def __init__(self):
        super().__init__("markers")

    def draw(self, surface: pygame.Surface, context):
        marker_renderer = context.marker_renderer
        marker_renderer.draw(surface)


# ------------------------------------------------------------
# LAYER MANAGER
# ------------------------------------------------------------

class LayerManager:
    """Manages ordering, visibility and drawing of all layers."""

    def __init__(self):
        self.layers: List[BaseLayer] = []

    def add_layer(self, layer: BaseLayer):
        self.layers.append(layer)

    def get_layer(self, name: str) -> Optional[BaseLayer]:
        for layer in self.layers:
            if layer.name == name:
                return layer
        return None

    def set_visible(self, name: str, state: bool):
        layer = self.get_layer(name)
        if layer:
            layer.set_visible(state)

    def draw(self, surface: pygame.Surface, context):
        """Draw layers in order."""
        for layer in self.layers:
            if layer.visible:
                layer.draw(surface, context)
