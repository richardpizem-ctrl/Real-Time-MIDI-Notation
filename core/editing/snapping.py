# SIRIUS CORE – Snapping Logic v2
# Pure mathematical snapping engine (no UI, no rendering)

from dataclasses import dataclass
from typing import Literal


SnapMode = Literal["beat", "bar", "custom"]


@dataclass
class SnapGrid:
    """Defines snapping resolution and mode."""
    resolution: float  # e.g., 0.25 for 1/4, 0.125 for 1/8
    mode: SnapMode = "beat"


def snap_time(time_value: float, grid: SnapGrid) -> float:
    """
    Snaps a time value to the nearest grid point.
    Example: time=1.13, resolution=0.25 → 1.25
    """
    if grid.resolution <= 0:
        return time_value  # invalid grid → no snapping

    steps = round(time_value / grid.resolution)
    return steps * grid.resolution


def snap_range(start: float, end: float, grid: SnapGrid) -> tuple[float, float]:
    """
    Snaps both start and end times.
    Ensures end >= start after snapping.
    """
    snapped_start = snap_time(start, grid)
    snapped_end = snap_time(end, grid)

    if snapped_end < snapped_start:
        snapped_end = snapped_start

    return snapped_start, snapped_end


def snap_pitch(pitch: int, semitone_step: int = 1) -> int:
    """
    Optional pitch snapping (CORE-level).
    Example: pitch=61, step=2 → 62
    """
    if semitone_step <= 0:
        return pitch

    steps = round(pitch / semitone_step)
    return steps * semitone_step
