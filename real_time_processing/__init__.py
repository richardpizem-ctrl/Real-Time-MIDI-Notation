# =========================================================
# Real-Time MIDI Notation – Real-Time Processing Module v4.0.0
# =========================================================
"""
Tento balík zabezpečuje:
- spracovanie MIDI udalostí v reálnom čase
- monitorovanie latencie a výkonu
- správu streamov a playback pipeline
- bezpečné spracovanie chýb počas real-time behu
- prepojenie na renderer a hlavný event bus

Modul je optimalizovaný pre nízku latenciu, stabilitu a predvídateľné správanie.
"""

from .error_handler import ErrorHandler
from .latency_monitor import LatencyMonitor
from .performance_tracker import PerformanceTracker
from .playback_engine import PlaybackEngine
from .stream_handler import StreamHandler

__all__ = [
    "ErrorHandler",
    "LatencyMonitor",
    "PerformanceTracker",
    "PlaybackEngine",
    "StreamHandler",
]

__version__ = "4.0.0"
