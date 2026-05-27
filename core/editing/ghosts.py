# SIRIUS CORE – Ghost & Hover Primitives
# CORE-only preview models for editing (no UI, no rendering)

from dataclasses import dataclass
from typing import Optional


@dataclass
class GhostNote:
    """Represents a preview note (ghost) before it is placed."""
    time: float
    pitch: int
    duration: float
    velocity: int = 64
    track_id: Optional[int] = None


@dataclass
class GhostRegion:
    """Represents a preview region before it is created."""
    start_time: float
    end_time: float
    track_id: Optional[int] = None


class HoverState:
    """
    CORE hover detection.
    UI will later visualize this, but CORE only tracks the state.
    """

    def __init__(self) -> None:
        self.hover_time: Optional[float] = None
        self.hover_pitch: Optional[int] = None
        self.hover_region: Optional[GhostRegion] = None

    def clear(self) -> None:
        self.hover_time = None
        self.hover_pitch = None
        self.hover_region = None

    def set_hover_time(self, t: float) -> None:
        self.hover_time = t

    def set_hover_pitch(self, p: int) -> None:
        self.hover_pitch = p

    def set_hover_region(self, region: GhostRegion) -> None:
        self.hover_region = region


class GhostController:
    """
    Manages ghost objects (notes, regions) for editing preview.
    """

    def __init__(self) -> None:
        self.current_note: Optional[GhostNote] = None
        self.current_region: Optional[GhostRegion] = None

    def show_note(self, note: GhostNote) -> None:
        self.current_note = note

    def hide_note(self) -> None:
        self.current_note = None

    def show_region(self, region: GhostRegion) -> None:
        self.current_region = region

    def hide_region(self) -> None:
        self.current_region = None
