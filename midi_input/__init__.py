"""
Real-Time MIDI Notation – MIDI Input Module

Tento balík zabezpečuje:
- inicializáciu MIDI zariadení
- real-time príjem MIDI udalostí
- normalizáciu a preposielanie do EventBusu
- detekciu chýb, reconnect a bezpečné ukončenie

Modul je navrhnutý pre nízku latenciu a stabilitu.
"""

from .midi_listener import MidiListener
from .midi_device import MidiDevice
from .midi_scanner import MidiScanner
from .midi_message import MidiMessage
from .input_manager import InputManager

__all__ = [
    "MidiListener",
    "MidiDevice",
    "MidiScanner",
    "MidiMessage",
    "InputManager",
]

__version__ = "3.0.0"

