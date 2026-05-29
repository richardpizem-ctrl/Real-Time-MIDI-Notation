# =========================================================
# test_editing_regions.py – v4.3.0
# Základné testy CORE region editing (RegionManager v4.3.0)
# =========================================================

from core.editing.regions import RegionManager, EditRegion


def test_region_create_and_split():
    mgr = RegionManager()

    r = mgr.create_region(0.0, 4.0, track_id=0)
    assert isinstance(r, EditRegion)
    assert r.start_time == 0.0
    assert r.end_time == 4.0
    assert r.track_id == 0

    split = mgr.split_region(r, 2.0)
    assert len(split) == 2

    left, right = split
    assert left.start_time == 0.0
    assert left.end_time == 2.0
    assert right.start_time == 2.0
    assert right.end_time == 4.0


def test_region_invalid_split():
    mgr = RegionManager()
    r = mgr.create_region(0.0, 4.0)

    # Split outside region → should return original
    split = mgr.split_region(r, -1.0)
    assert split == [r]

    split = mgr.split_region(r, 10.0)
    assert split == [r]


def test_region_merge():
    mgr = RegionManager()

    a = mgr.create_region(0.0, 2.0, track_id=1)
    b = mgr.create_region(2.0, 5.0, track_id=1)

    merged = mgr.merge_regions(a, b)
    assert isinstance(merged, EditRegion)
    assert merged.start_time == 0.0
    assert merged.end_time == 5.0
    assert merged.track_id == 1


def test_region_merge_invalid_track():
    mgr = RegionManager()

    a = mgr.create_region(0.0, 2.0, track_id=1)
    b = mgr.create_region(2.0, 5.0, track_id=2)

    merged = mgr.merge_regions(a, b)
    assert merged is None  # cannot merge across tracks
