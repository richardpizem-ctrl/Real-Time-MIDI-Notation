# =========================================================
# SIRIUS CORE – Ghost & Hover Primitives (v4.3.0)
# CORE-only preview models for editing (no UI, no rendering)
# Real-time safe, deterministic, minimal memory footprint
# =========================================================

from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------
# GHOST NOTE
# ---------------------------------------------------------
@dataclass(slots=True)
class GhostNote:
    """Represents a preview note (ghost) before it is placed."""
    time: float
    pitch: int
    duration: float
    velocity: int = 64
    track_id: Optional[int] = None


# ---------------------------------------------------------
# GHOST REGION
# ---------------------------------------------------------
@dataclass(slots=True)
class GhostRegion:
    """Represents a preview region before it is created."""
    start_time: float
    end_time: float
    track_id: Optional[int] = None


# ---------------------------------------------------------
# HOVER STATE
# ---------------------------------------------------------
class HoverState:
    """
    CORE hover detection.
    UI will later visualize this, but CORE only tracks the state.
    """

    __slots__ = ("hover_time", "hover_pitch", "hover_region")

    def __init__(self) -> None:
        self.hover_time: Optional[float] = None
        self.hover_pitch: Optional[int] = None
        self.hover_region: Optional[GhostRegion] = None

    def clear(self) -> None:
        self.hover_time = None
        self.hover_pitch = None
        self.hover_region = None

    def set_hover_time(self, t: float) -> None:
        try:
            self.hover_time = float(t)
        except Exception:
            self.hover_time = None

    def set_hover_pitch(self, p: int) -> None:
        try:
            self.hover_pitch = int(p)
        except Exception:
            self.hover_pitch = None

    def set_hover_region(self, region: GhostRegion) -> None:
        self.hover_region = region


# ---------------------------------------------------------
# GHOST CONTROLLER
# ---------------------------------------------------------
class GhostController:
    """
    Manages ghost objects (notes, regions) for editing preview.
    """

    __slots__ = ("current_note", "current_region")

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
