# =========================================================
# SIRIUS CORE – Selection Model v2 (v4.3.0)
# CORE-only selection primitives (no UI)
# Real-time safe, deterministic, minimal memory footprint
# =========================================================

from dataclasses import dataclass
from typing import List, Optional


# ---------------------------------------------------------
# SELECTION ITEM
# ---------------------------------------------------------
@dataclass(slots=True)
class SelectionItem:
    track_id: Optional[int]
    start_time: float
    end_time: float
    pitch: Optional[int] = None

    def duration(self) -> float:
        try:
            return max(0.0, float(self.end_time) - float(self.start_time))
        except Exception:
            return 0.0

    def is_valid(self) -> bool:
        try:
            return float(self.end_time) > float(self.start_time)
        except Exception:
            return False


# ---------------------------------------------------------
# SELECTION SET
# ---------------------------------------------------------
class SelectionSet:
    """
    SelectionSet (v4.3.0):
    - drží SelectionItem objekty
    - real-time safe
    - žiadne UI závislosti
    - kompatibilné so selection_actions v4.3.0
    """

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: List[SelectionItem] = []

    # -----------------------------------------------------
    # CLEAR
    # -----------------------------------------------------
    def clear(self) -> None:
        self._items.clear()

    # -----------------------------------------------------
    # ADD
    # -----------------------------------------------------
    def add(self, item: SelectionItem) -> None:
        if isinstance(item, SelectionItem) and item.is_valid():
            self._items.append(item)

    # -----------------------------------------------------
    # REMOVE
    # -----------------------------------------------------
    def remove(self, item: SelectionItem) -> None:
        try:
            self._items.remove(item)
        except Exception:
            pass

    # -----------------------------------------------------
    # GET ALL
    # -----------------------------------------------------
    def get_all(self) -> List[SelectionItem]:
        return list(self._items)

    # -----------------------------------------------------
    # QUERY HELPERS
    # -----------------------------------------------------
    def get_by_track(self, track_id: int) -> List[SelectionItem]:
        return [i for i in self._items if i.track_id == track_id]

    def get_time_range(self) -> Optional[tuple]:
        if not self._items:
            return None
        try:
            start = min(i.start_time for i in self._items)
            end = max(i.end_time for i in self._items)
            return (start, end)
        except Exception:
            return None

    def is_empty(self) -> bool:
        return len(self._items) == 0
