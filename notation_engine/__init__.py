"""
Real-Time MIDI Notation – Notation Engine Module (v4.3.0)

Tento balík obsahuje všetky analytické a spracovacie vrstvy potrebné na:
- mapovanie MIDI udalostí na noty
- detekciu rytmu, harmónie, akordov a tóniny
- generovanie symbolov a grafických prvkov
- real-time rozloženie notového zápisu
- prepojenie s rendererom a real-time processing pipeline

Notation Engine je centrálna analytická vrstva systému.
"""

from .note_mapper import NoteMapper
from .midi_note_mapper import MidiNoteMapper
from .rhythm_analyzer import RhythmAnalyzer
from .harmony_engine import HarmonyEngine
from .chord_detector import ChordDetector
from .scale_detector import ScaleDetector
from .key_detector import KeyDetector
from .drum_notation import DrumNotation
from .symbol_manager import SymbolManager
from .layout_engine import LayoutEngine
from .notation_processor import NotationProcessor
from .notation_renderer import NotationRenderer

__all__ = [
    "NoteMapper",
    "MidiNoteMapper",
    "RhythmAnalyzer",
    "HarmonyEngine",
    "ChordDetector",
    "ScaleDetector",
    "KeyDetector",
    "DrumNotation",
    "SymbolManager",
    "LayoutEngine",
    "NotationProcessor",
    "NotationRenderer",
]

__version__ = "4.3.0"
