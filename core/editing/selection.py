# CORE selection model v2

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SelectionItem:
    track_id: Optional[int]
    start_time: float
    end_time: float
    pitch: Optional[int] = None


class SelectionSet:
    def __init__(self) -> None:
        self._items: List[SelectionItem] = []

    def clear(self) -> None:
        self._items.clear()

    def add(self, item: SelectionItem) -> None:
        self._items.append(item)

    def get_all(self) -> List[SelectionItem]:
        return list(self._items)
