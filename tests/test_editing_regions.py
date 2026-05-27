# Basic tests for CORE region editing

from core.editing.regions import RegionManager


def test_region_create_and_split():
    mgr = RegionManager()

    r = mgr.create_region(0.0, 4.0, track_id=0)
    assert r.start_time == 0.0
    assert r.end_time == 4.0

    split = mgr.split_region(r, 2.0)
    assert len(split) == 2
    left, right = split

    assert left.start_time == 0.0
    assert left.end_time == 2.0
    assert right.start_time == 2.0
    assert right.end_time == 4.0
