# Basic tests for CORE ghost primitives

from core.editing.ghosts import GhostNote, GhostRegion, GhostController, HoverState


def test_ghost_note_basic():
    g = GhostNote(time=1.0, pitch=60, duration=0.5, velocity=90)
    assert g.time == 1.0
    assert g.pitch == 60
    assert g.duration == 0.5
    assert g.velocity == 90


def test_ghost_controller_basic():
    ctrl = GhostController()
    assert ctrl.current_note is None

    note = GhostNote(time=0.0, pitch=64, duration=1.0)
    ctrl.show_note(note)
    assert ctrl.current_note is not None

    ctrl.hide_note()
    assert ctrl.current_note is None


def test_hover_state_basic():
    hover = HoverState()
    hover.set_hover_time(1.5)
    hover.set_hover_pitch(62)

    assert hover.hover_time == 1.5
    assert hover.hover_pitch == 62

    hover.clear()
    assert hover.hover_time is None
    assert hover.hover_pitch is None
