# =========================================================
# test_editing_selection.py – v4.3.0
# Základné testy CORE selection model v2 (SelectionSet, SelectionItem)
# Kompatibilné s Editing Module v4.3.0
# =========================================================

from core.editing.selection import SelectionSet, SelectionItem


def test_selection_add_and_clear():
    sel = SelectionSet()
    assert sel.is_empty()

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
    assert sel.is_empty()


def test_selection_get_by_track():
    sel = SelectionSet()

    sel.add(SelectionItem(track_id=0, start_time=0.0, end_time=1.0))
    sel.add(SelectionItem(track_id=1, start_time=1.0, end_time=2.0))
    sel.add(SelectionItem(track_id=0, start_time=2.0, end_time=3.0))

    track0 = sel.get_by_track(0)
    assert len(track0) == 2

    track1 = sel.get_by_track(1)
    assert len(track1) == 1


def test_selection_time_range():
    sel = SelectionSet()

    sel.add(SelectionItem(track_id=0, start_time=5.0, end_time=6.0))
    sel.add(SelectionItem(track_id=0, start_time=1.0, end_time=2.0))
    sel.add(SelectionItem(track_id=0, start_time=3.0, end_time=4.0))

    start, end = sel.get_time_range()
    assert start == 1.0
    assert end == 6.0


def test_selection_invalid_item_is_ignored():
    sel = SelectionSet()

    # end_time < start_time → invalid
    invalid = SelectionItem(track_id=0, start_time=5.0, end_time=1.0)
    sel.add(invalid)

    assert sel.is_empty()
