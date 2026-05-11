# =========================================================
# EventBus v4.0.0 – Stable, safe, thread‑safe event system
# =========================================================

import threading
from collections import defaultdict
from typing import Callable, Any, Dict, List

from core.logger import Logger


class EventBus:
    """
    EventBus (v4.0.0)
    -----------------
    Stable, safe, thread‑safe event router for the entire system.

    Features:
        - subscribe(event_type, callback)
        - unsubscribe(event_type, callback)
        - publish(event_type, data)
        - publish_async(event_type, data)

    Properties:
        - no exceptions leak out
        - callbacks executed outside lock (no deadlocks)
        - validation of event types and callbacks
        - ready for v5 (AI/TIMELINE hooks, async pipelines)
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()

        try:
            Logger.info("EventBus initialized (v4.0.0).")
        except Exception:
            pass

    # ---------------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------------
    def _validate_event_type(self, event_type: str) -> bool:
        if not isinstance(event_type, str) or not event_type.strip():
            try:
                Logger.error("EventBus: invalid event_type")
            except Exception:
                pass
            return False
        return True

    def _validate_callback(self, callback) -> bool:
        if not callable(callback):
            try:
                Logger.error("EventBus: callback is not callable")
            except Exception:
                pass
            return False
        return True

    # ---------------------------------------------------------
    # SUBSCRIBE
    # ---------------------------------------------------------
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Register a callback for the given event type."""
        if not self._validate_event_type(event_type):
            return
        if not self._validate_callback(callback):
            return

        try:
            with self._lock:
                if callback not in self._subscribers[event_type]:
                    self._subscribers[event_type].append(callback)
                    Logger.debug(f"Subscribed to event '{event_type}'")
        except Exception:
            pass

    # ---------------------------------------------------------
    # UNSUBSCRIBE
    # ---------------------------------------------------------
    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Remove a callback from the given event type."""
        if not self._validate_event_type(event_type):
            return
        if not self._validate_callback(callback):
            return

        try:
            with self._lock:
                if callback in self._subscribers[event_type]:
                    self._subscribers[event_type].remove(callback)
                    Logger.debug(f"Unsubscribed from event '{event_type}'")

                if not self._subscribers[event_type]:
                    del self._subscribers[event_type]
        except Exception:
            pass

    # ---------------------------------------------------------
    # SYNCHRONOUS PUBLISH
    # ---------------------------------------------------------
    def publish(self, event_type: str, data: Any = None) -> None:
        """Synchronously dispatch event to all subscribers."""
        if not self._validate_event_type(event_type):
            return

        try:
            with self._lock:
                callbacks = list(self._subscribers.get(event_type, []))
        except Exception:
            callbacks = []

        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                try:
                    Logger.error(f"[EventBus] Error in callback for '{event_type}': {e}")
                except Exception:
                    pass

    # ---------------------------------------------------------
    # ASYNCHRONOUS PUBLISH
    # ---------------------------------------------------------
    def publish_async(self, event_type: str, data: Any = None) -> None:
        """Asynchronously dispatch event in a separate thread."""
        if not self._validate_event_type(event_type):
            return

        try:
            thread = threading.Thread(
                target=self.publish,
                args=(event_type, data),
                daemon=True
            )
            thread.start()

            Logger.debug(f"Async publish scheduled for event '{event_type}'")
        except Exception:
            pass

    # ---------------------------------------------------------
    # NO-OP API (UI compatibility)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
