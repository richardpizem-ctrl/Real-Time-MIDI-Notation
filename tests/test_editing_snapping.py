# Basic tests for CORE snapping logic

from core.editing.snapping import SnapGrid, snap_time, snap_range


def test_snap_time_basic():
    grid = SnapGrid(0.25)  # 1/4 beat
    assert snap_time(1.13, grid) == 1.25
    assert snap_time(0.12, grid) == 0.0


def test_snap_range_basic():
    grid = SnapGrid(0.5)
    start, end = snap_range(0.3, 1.2, grid)

    # start musí byť snapnutý na 0.5
    assert start == 0.5

    # end môže byť 1.0 alebo 1.5 podľa rounding
    assert end in (1.0, 1.5)
