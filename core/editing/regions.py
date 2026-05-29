# =========================================================
# SIRIUS CORE – Region Editing Groundwork (v4.3.0)
# CORE-only region model for editing operations (no UI)
# Real-time safe, deterministic, minimal memory footprint
# =========================================================

from dataclasses import dataclass
from typing import Optional, List


# ---------------------------------------------------------
# REGION MODEL
# ---------------------------------------------------------
@dataclass(slots=True)
class EditRegion:
    """Represents a logical editing region in the timeline."""
    start_time: float
    end_time: float
    track_id: Optional[int] = None
    label: Optional[str] = None

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
# REGION MANAGER
# ---------------------------------------------------------
class RegionManager:
    """
    Manages creation, splitting, merging and validation of regions.
    Real-time safe, deterministic, CORE-only.
    """

    __slots__ = ("_regions",)

    def __init__(self) -> None:
        self._regions: List[EditRegion] = []

    # -----------------------------------------------------
    # CREATE
    # -----------------------------------------------------
    def create_region(self, start: float, end: float, track_id: Optional[int] = None) -> EditRegion:
        try:
            start = float(start)
            end = float(end)
        except Exception:
            start, end = 0.0, 0.0

        region = EditRegion(start, end, track_id)
        self._regions.append(region)
        return region

    # -----------------------------------------------------
    # SPLIT
    # -----------------------------------------------------
    def split_region(self, region: EditRegion, split_time: float) -> List[EditRegion]:
        """Splits a region into two at split_time. Returns new regions or original."""
        try:
            split_time = float(split_time)
        except Exception:
            return [region]

        if split_time <= region.start_time or split_time >= region.end_time:
            return [region]  # invalid split → return original

        left = EditRegion(region.start_time, split_time, region.track_id, region.label)
        right = EditRegion(split_time, region.end_time, region.track_id, region.label)

        try:
            self._regions.remove(region)
        except Exception:
            pass

        self._regions.extend([left, right])
        return [left, right]

    # -----------------------------------------------------
    # MERGE
    # -----------------------------------------------------
    def merge_regions(self, a: EditRegion, b: EditRegion) -> Optional[EditRegion]:
        """Merges two adjacent or overlapping regions."""
        if a.track_id != b.track_id:
            return None  # cannot merge across tracks

        start = min(a.start_time, b.start_time)
        end = max(a.end_time, b.end_time)

        merged = EditRegion(start, end, a.track_id, a.label)

        # remove originals safely
        for r in (a, b):
            try:
                self._regions.remove(r)
            except Exception:
                pass

        self._regions.append(merged)
        return merged

    # -----------------------------------------------------
    # GET ALL
    # -----------------------------------------------------
    def get_all(self) -> List[EditRegion]:
        return list(self._regions)
