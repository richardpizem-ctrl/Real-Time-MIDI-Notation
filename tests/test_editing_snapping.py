# =========================================================
# test_editing_snapping.py – v4.3.0
# Základné testy CORE snapping logic (SnapGrid, snap_time, snap_range)
# Kompatibilné so Snapping Engine v4.3.0
# =========================================================

from core.editing.snapping import SnapGrid, snap_time, snap_range, SnapEngine


def test_snap_time_basic():
    grid = SnapGrid(0.25)  # 1/4 beat
    assert snap_time(1.13, grid) == 1.25
    assert snap_time(0.12, grid) == 0.0


def test_snap_range_basic():
    grid = SnapGrid(0.5)
    start, end = snap_range(0.3, 1.2, grid)

    assert start == 0.5
    assert end in (1.0, 1.5)


def test_snap_engine_beat_mode():
    engine = SnapEngine(SnapGrid(0.25, mode="beat"))
    assert engine.snap(1.13) == 1.25
    assert engine.snap(0.12) == 0.0


def test_snap_engine_custom_mode():
    engine = SnapEngine(SnapGrid(0.3, mode="custom"))
    assert engine.snap(1.0) == 0.9
    assert engine.snap(1.14) == 1.2


def test_snap_engine_bar_mode():
    grid = SnapGrid(resolution=1.0, mode="bar", bar_length=4.0)
    engine = SnapEngine(grid)

    assert engine.snap(3.2) == 4.0
    assert engine.snap(6.9) == 8.0


def test_snap_range_engine():
    engine = SnapEngine(SnapGrid(0.5))
    s, e = engine.snap_range(0.3, 1.2)

    assert s == 0.5
    assert e in (1.0, 1.5)
