# =========================================================
# Real-Time MIDI Notation – Real-Time Processing Module v4.3.0
# =========================================================
"""
Tento balík zabezpečuje:
- spracovanie MIDI udalostí v reálnom čase
- monitorovanie latencie a výkonu
- správu streamov a playback pipeline
- bezpečné spracovanie chýb počas real-time behu
- prepojenie na renderer, Notation Engine a hlavný event bus

Modul je optimalizovaný pre nízku latenciu, stabilitu a predvídateľné správanie.
Verzia 4.3.0 je pripravená pre Runtime 4.x → 5.x a renderer_new.
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

__version__ = "4.3.0"
