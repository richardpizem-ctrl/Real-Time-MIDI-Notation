# =========================================================
# SIRIUS CORE – Editing module (v4.3.0)
# Non‑UI editing primitives:
# - Selection Model v2
# - Region Editing v1.5
# - Snapping Engine v2
# - Ghost Primitives (Preview Models)
# Stabilná verzia pre Runtime 4.3.0 → 5.x
# =========================================================

from .selection import SelectionSet, SelectionItem
from .snapping import SnapEngine, SnapResult
from .regions import Region, RegionSet
from .ghosts import GhostNote, GhostRegion

__all__ = [
    "SelectionSet",
    "SelectionItem",
    "SnapEngine",
    "SnapResult",
    "Region",
    "RegionSet",
    "GhostNote",
    "GhostRegion",
]

__version__ = "4.3.0"
