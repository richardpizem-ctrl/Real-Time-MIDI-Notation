# Event bus

import threading
from collections import defaultdict

class EventBus:
    def __init__(self):
        self._subscribers = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type, callback):
        """Register a callback for a specific event type."""
        with self._lock:
            self._subscribers[event_type].append(callback)

    def publish(self, event_type, data=None):
        """Send an event to all subscribers."""
        with self._lock:
            callbacks = list(self._subscribers[event_type])

        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"[EventBus] Error in callback for '{event_type}': {e}")

