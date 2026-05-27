# SIRIUS CORE – Region Editing Groundwork
# CORE-only region model for editing operations (no UI, no rendering)

from dataclasses import dataclass
from typing import Optional, List


@dataclass
class EditRegion:
    """Represents a logical editing region in the timeline."""
    start_time: float
    end_time: float
    track_id: Optional[int] = None
    label: Optional[str] = None

    def duration(self) -> float:
        return max(0.0, self.end_time - self.start_time)


class RegionManager:
    """Manages creation, splitting, merging and validation of regions."""

    def __init__(self) -> None:
        self._regions: List[EditRegion] = []

    def create_region(self, start: float, end: float, track_id: Optional[int] = None) -> EditRegion:
        region = EditRegion(start, end, track_id)
        self._regions.append(region)
        return region

    def split_region(self, region: EditRegion, split_time: float) -> List[EditRegion]:
        """Splits a region into two at split_time."""
        if split_time <= region.start_time or split_time >= region.end_time:
            return [region]  # invalid split → return original

        left = EditRegion(region.start_time, split_time, region.track_id, region.label)
        right = EditRegion(split_time, region.end_time, region.track_id, region.label)

        # replace original
        self._regions.remove(region)
        self._regions.extend([left, right])

        return [left, right]

    def merge_regions(self, a: EditRegion, b: EditRegion) -> Optional[EditRegion]:
        """Merges two adjacent or overlapping regions."""
        if a.track_id != b.track_id:
            return None  # cannot merge across tracks

        start = min(a.start_time, b.start_time)
        end = max(a.end_time, b.end_time)

        merged = EditRegion(start, end, a.track_id, a.label)

        # remove originals
        self._regions.remove(a)
        self._regions.remove(b)
        self._regions.append(merged)

        return merged

    def get_all(self) -> List[EditRegion]:
        return list(self._regions)
