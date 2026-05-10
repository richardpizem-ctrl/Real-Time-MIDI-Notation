"""
Real-Time MIDI Notation – Core Module

Toto jadro poskytuje základné stavebné bloky pre:
- real-time MIDI input
- event routing a scheduling
- spracovanie udalostí s nízkou latenciou
- prepojenie na notation engine a renderer

Balík core slúži ako centrálna vrstva celej real-time pipeline.
"""

from .event_types import MidiEvent
from .event_bus import EventBus
from .playback_engine import PlaybackEngine
from .track_manager import TrackManager
from .notation_processor import NotationProcessor
from .config_manager import ConfigManager
from .logger import Logger

__all__ = [
    "MidiEvent",
    "EventBus",
    "PlaybackEngine",
    "TrackManager",
    "NotationProcessor",
    "ConfigManager",
    "Logger",
]

# verzia balíka (lokálna, bez pyproject)
__version__ = "3.0.0"
# Core module
