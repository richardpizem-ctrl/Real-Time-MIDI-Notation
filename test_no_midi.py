# =========================================================
# test_no_midi.py v4.0.0
# Test: system must work even without a MIDI device
# =========================================================

import pytest
from real_time_processing.midi_input import MidiInput


def test_midi_initialization_without_device():
    """
    Ensure MidiInput initializes even when no MIDI device is present.
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
    poll_events() must always return a list,
    even when no MIDI device is connected.
    """
    midi = MidiInput()

    try:
        events = midi.poll_events()
    except Exception as e:
        pytest.fail(f"poll_events() raised exception: {e}")

    assert isinstance(events, list)


def test_poll_events_safe_behavior():
    """
    poll_events() must never raise an exception,
    even when no MIDI device exists.
    """
    midi = MidiInput()

    for _ in range(5):
        try:
            events = midi.poll_events()
        except Exception as e:
            pytest.fail(f"poll_events() threw exception: {e}")

        assert isinstance(events, list)
