"""
Real-Time MIDI Notation – MIDI Input Module (v4.3.0)

Tento balík zabezpečuje:
- inicializáciu MIDI zariadení
- real-time príjem MIDI udalostí
- normalizáciu a preposielanie do EventBusu
- detekciu chýb, reconnect a bezpečné ukončenie
- stabilnú integráciu s Real-Time Processing v4.3.0

Modul je navrhnutý pre nízku latenciu, stabilitu a deterministické správanie.
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

__version__ = "4.3.0"
