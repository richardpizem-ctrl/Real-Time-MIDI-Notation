# =========================================================
# SIRIUS CORE – Snapping Logic v2 (v4.3.0)
# Pure mathematical snapping engine (no UI, no rendering)
# Real-time safe, deterministic, minimal memory footprint
# =========================================================

from dataclasses import dataclass
from typing import Literal, Optional


SnapMode = Literal["beat", "bar", "custom"]


# ---------------------------------------------------------
# SNAP GRID
# ---------------------------------------------------------
@dataclass(slots=True)
class SnapGrid:
    """Defines snapping resolution and mode."""
    resolution: float          # e.g., 0.25 for 1/4, 0.125 for 1/8
    mode: SnapMode = "beat"
    bar_length: Optional[float] = None   # used only for mode="bar"


# ---------------------------------------------------------
# PURE SNAP FUNCTIONS
# ---------------------------------------------------------
def snap_time(time_value: float, grid: SnapGrid) -> float:
    """
    Snaps a time value to the nearest grid point.
    Example: time=1.13, resolution=0.25 → 1.25
    Real-time safe.
    """
    try:
        t = float(time_value)
    except Exception:
        return time_value

    try:
        res = float(grid.resolution)
    except Exception:
        return t

    if res <= 0:
        return t

    steps = round(t / res)
    return steps * res


def snap_range(start: float, end: float, grid: SnapGrid) -> tuple[float, float]:
    """
    Snaps both start and end times.
    Ensures end >= start after snapping.
    """
    s = snap_time(start, grid)
    e = snap_time(end, grid)

    if e < s:
        e = s

    return s, e


def snap_pitch(pitch: int, semitone_step: int = 1) -> int:
    """
    Optional pitch snapping (CORE-level).
    Example: pitch=61, step=2 → 62
    """
    try:
        p = int(pitch)
    except Exception:
        return pitch

    try:
        step = int(semitone_step)
    except Exception:
        return p

    if step <= 0:
        return p

    steps = round(p / step)
    return steps * step


# ---------------------------------------------------------
# SNAP ENGINE (v4.3.0)
# ---------------------------------------------------------
class SnapEngine:
    """
    High-level snapping engine for CORE editing.
    Supports:
        - beat snapping
        - bar snapping
        - custom snapping
    """

    __slots__ = ("grid",)

    def __init__(self, grid: SnapGrid) -> None:
        self.grid = grid

    # -----------------------------------------------------
    # TIME SNAP
    # -----------------------------------------------------
    def snap(self, time_value: float) -> float:
        """Snaps a single time value according to grid.mode."""
        mode = self.grid.mode

        if mode == "beat":
            return snap_time(time_value, self.grid)

        if mode == "custom":
            return snap_time(time_value, self.grid)

        if mode == "bar":
            try:
                bar_len = float(self.grid.bar_length)
            except Exception:
                return snap_time(time_value, self.grid)

            if bar_len <= 0:
                return snap_time(time_value, self.grid)

            steps = round(time_value / bar_len)
            return steps * bar_len

        # fallback
        return snap_time(time_value, self.grid)

    # -----------------------------------------------------
    # RANGE SNAP
    # -----------------------------------------------------
    def snap_range(self, start: float, end: float) -> tuple[float, float]:
        """Snaps a time range according to grid.mode."""
        s = self.snap(start)
        e = self.snap(end)
        if e < s:
            e = s
        return s, e

    # -----------------------------------------------------
    # PITCH SNAP
    # -----------------------------------------------------
    def snap_pitch(self, pitch: int, step: int = 1) -> int:
        return snap_pitch(pitch, step)
