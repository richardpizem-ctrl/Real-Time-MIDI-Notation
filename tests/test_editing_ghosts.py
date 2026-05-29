# =========================================================
# test_editing_ghosts.py – v4.3.0
# Základné testy CORE ghost primitives (GhostNote, GhostRegion,
# GhostController, HoverState)
# Kompatibilné s Editing Module v4.3.0
# =========================================================

from core.editing.ghosts import GhostNote, GhostRegion, GhostController, HoverState


def test_ghost_note_basic():
    g = GhostNote(time=1.0, pitch=60, duration=0.5, velocity=90)
    assert g.time == 1.0
    assert g.pitch == 60
    assert g.duration == 0.5
    assert g.velocity == 90
    assert g.track_id is None


def test_ghost_region_basic():
    r = GhostRegion(start_time=0.0, end_time=2.0, track_id=1)
    assert r.start_time == 0.0
    assert r.end_time == 2.0
    assert r.track_id == 1


def test_ghost_controller_basic():
    ctrl = GhostController()
    assert ctrl.current_note is None
    assert ctrl.current_region is None

    note = GhostNote(time=0.0, pitch=64, duration=1.0)
    ctrl.show_note(note)
    assert ctrl.current_note is note

    ctrl.hide_note()
    assert ctrl.current_note is None

    region = GhostRegion(start_time=1.0, end_time=3.0)
    ctrl.show_region(region)
    assert ctrl.current_region is region

    ctrl.hide_region()
    assert ctrl.current_region is None


def test_hover_state_basic():
    hover = HoverState()

    hover.set_hover_time(1.5)
    hover.set_hover_pitch(62)

    assert hover.hover_time == 1.5
    assert hover.hover_pitch == 62
    assert hover.hover_region is None

    region = GhostRegion(start_time=0.0, end_time=1.0)
    hover.set_hover_region(region)
    assert hover.hover_region is region

    hover.clear()
    assert hover.hover_time is None
    assert hover.hover_pitch is None
    assert hover.hover_region is None
