"""Canonical MIDI input."""
from .message_parser import MessageParser
from .midi_listener import MIDIListener
MidiListener = MIDIListener
__all__ = ['MessageParser', 'MIDIListener', 'MidiListener']
