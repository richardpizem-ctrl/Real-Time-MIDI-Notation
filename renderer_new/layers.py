import pygame
from typing import List, Optional

from .timeline_layer import TimelineLayer
from .selection_layer import SelectionLayer
from .notes_layer import NotesLayer
from .playhead_layer import PlayheadLayer
from .marker_layer import MarkerLayer


class BaseLayer:
    """
    Základná vrstva pre renderer – FÁZA 4.
    Každá vrstva musí implementovať:
        - draw(surface)
        - visible (bool)
        - z_index (poradie vykresľovania)
    """

    def __init__(self, z_index: int = 0, visible: bool = True):
        self.z_index = z_index
        self.visible = visible

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError("Layer must implement draw().")


class LayerManager:
    """
    LayerManager – riadi všetky vrstvy renderera.
    FÁZA 4 – stabilizované, modulárne, bezpečné.
    """

    def __init__(self):
        self.layers: List[BaseLayer] = []

    # ---------------------------------------------------------
    # REGISTRÁCIA VRSTIEV
    # ---------------------------------------------------------
    def add_layer(self, layer: BaseLayer):
        """Pridá vrstvu a zoradí podľa z-indexu."""
        self.layers.append(layer)
        self.layers.sort(key=lambda l: l.z_index)

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface):
        """Vykreslí všetky viditeľné vrstvy v správnom poradí."""
        for layer in self.layers:
            if layer.visible:
                try:
                    layer.draw(surface)
                except Exception:
                    pass


# -------------------------------------------------------------
# FACTORY – vytvorenie kompletného setu vrstiev pre renderer
# -------------------------------------------------------------
def create_default_layers(controller) -> LayerManager:
    """
    Vytvorí kompletný balík vrstiev pre graphic_renderer.py.
    Poradie vrstiev (z-index):
        0 – TimelineLayer
        1 – NotesLayer
        2 – MarkerLayer
        3 – PlayheadLayer
        4 – SelectionLayer (overlay)
    """

    manager = LayerManager()

    manager.add_layer(TimelineLayer(controller, z_index=0))
    manager.add_layer(NotesLayer(controller, z_index=1))
    manager.add_layer(MarkerLayer(controller, z_index=2))
    manager.add_layer(PlayheadLayer(controller, z_index=3))
    manager.add_layer(SelectionLayer(controller, z_index=4))

    return manager
