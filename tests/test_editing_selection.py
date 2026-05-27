# Basic tests for CORE editing selection model

from core.editing.selection import SelectionSet, SelectionItem


def test_selection_add_and_clear():
    sel = SelectionSet()
    assert len(sel.get_all()) == 0

    item = SelectionItem(
        track_id=0,
        start_time=0.0,
        end_time=1.0,
        pitch=60,
    )
    sel.add(item)

    all_items = sel.get_all()
    assert len(all_items) == 1
    assert all_items[0].pitch == 60

    sel.clear()
    assert len(sel.get_all()) == 0
