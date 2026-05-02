# =========================================================
# test_no_midi.py v2.0.0
# Test: systém musí fungovať aj bez MIDI zariadenia
# =========================================================

import pytest
from real_time_processing.midi_input import MidiInput


def test_midi_initialization_without_device():
    """
    Testuje, že MidiInput sa inicializuje aj keď nie je
    pripojené žiadne MIDI zariadenie.
    """
    midi = None

    try:
        midi = MidiInput()
    except Exception as e:
        pytest.fail(f"MidiInput initialization failed without device: {e}")

    assert midi is not None
    assert hasattr(midi, "poll_events")


def test_poll_events_returns_list():
    """
    poll_events() musí vždy vrátiť list,
    aj keď nie je žiadne MIDI zariadenie.
    """
    midi = MidiInput()

    try:
        events = midi.poll_events()
    except Exception as e:
        pytest.fail(f"poll_events() raised exception: {e}")

    assert isinstance(events, list)


def test_poll_events_safe_behavior():
    """
    poll_events() nesmie nikdy vyhodiť výnimku,
    ani pri neexistujúcom MIDI zariadení.
    """
    midi = MidiInput()

    for _ in range(5):
        try:
            events = midi.poll_events()
        except Exception as e:
            pytest.fail(f"poll_events() threw exception: {e}")

        assert isinstance(events, list)
