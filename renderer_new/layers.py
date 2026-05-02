# =========================================================
# layers.py – Layer System v2.0.0
# Stabilný, modulárny, bezpečný systém vrstiev pre renderer
# =========================================================

import pygame
from typing import List, Optional

from .timeline_layer import TimelineLayer
from .selection_layer import SelectionLayer
from .notes_layer import NotesLayer
from .playhead_layer import PlayheadLayer
from .marker_layer import MarkerLayer


# ---------------------------------------------------------
# BASE LAYER
# ---------------------------------------------------------

class BaseLayer:
    """
    BaseLayer (v2.0.0)
    - Každá vrstva musí implementovať draw(surface)
    - Má vlastný z_index (poradie vykresľovania)
    - Má visible flag (zapnutie/vypnutie)
    - Stabilné, bezpečné, pripravené na v3
    """

    def __init__(self, z_index: int = 0, visible: bool = True):
        try:
            self.z_index = int(z_index)
        except Exception:
            self.z_index = 0

        self.visible = bool(visible)

    def draw(self, surface: pygame.Surface):
        raise NotImplementedError("Layer must implement draw().")


# ---------------------------------------------------------
# LAYER MANAGER
# ---------------------------------------------------------

class LayerManager:
    """
    LayerManager (v2.0.0)
    - riadi všetky vrstvy renderera
    - stabilné z-index triedenie
    - bezpečné vykresľovanie
    - pripravené na dynamické vrstvy vo v3
    """

    def __init__(self):
        self.layers: List[BaseLayer] = []

    # ---------------------------------------------------------
    # REGISTRÁCIA VRSTIEV
    # ---------------------------------------------------------
    def add_layer(self, layer: BaseLayer):
        """Pridá vrstvu a zoradí podľa z-indexu."""
        if not isinstance(layer, BaseLayer):
            return

        self.layers.append(layer)

        try:
            self.layers.sort(key=lambda l: l.z_index)
        except Exception:
            # fallback – ak by sort zlyhal
            self.layers = sorted(self.layers, key=lambda l: getattr(l, "z_index", 0))

    # ---------------------------------------------------------
    # RENDER
    # ---------------------------------------------------------
    def render(self, surface: pygame.Surface):
        """
        Vykreslí všetky viditeľné vrstvy v správnom poradí.
        Každá vrstva je izolovaná try/except blokom.
        """
        for layer in self.layers:
            if not layer.visible:
                continue

            try:
                layer.draw(surface)
            except Exception:
                # vrstva nesmie nikdy zhodiť renderer
                pass


# ---------------------------------------------------------
# FACTORY – vytvorenie kompletného setu vrstiev pre renderer
# ---------------------------------------------------------

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

    try:
        manager.add_layer(TimelineLayer(controller, z_index=0))
    except Exception:
        pass

    try:
        manager.add_layer(NotesLayer(controller, z_index=1))
    except Exception:
        pass

    try:
        manager.add_layer(MarkerLayer(controller, z_index=2))
    except Exception:
        pass

    try:
        manager.add_layer(PlayheadLayer(controller, z_index=3))
    except Exception:
        pass

    try:
        manager.add_layer(SelectionLayer(controller, z_index=4))
    except Exception:
        pass

    return manager
