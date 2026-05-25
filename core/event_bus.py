# =========================================================
# EventBus v4.1.0
# Stabilný, thread-safe event router pre Runtime 4.x–5.x
# =========================================================

import threading
from collections import defaultdict
from typing import Callable, Any, Dict, List
from .logger import Logger


class EventBus:
    """
    EventBus v4.1.0:
    - stabilný a deterministický
    - thread-safe publish
    - jednoduchý callback routing
    - pripravené pre Runtime 5.x (KG, Envoy, System Agent)
    """

    def __init__(self):
        Logger.info("Initializing EventBus (v4.1.0)...")

        self._subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()
        self._running = True

        Logger.info("EventBus initialized (v4.1.0).")

    # ---------------------------------------------------------
    # SUBSCRIBE / UNSUBSCRIBE
    # ---------------------------------------------------------
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if not isinstance(event_type, str):
            Logger.error("subscribe() called with non-string event_type")
            return

        if not callable(callback):
            Logger.error("subscribe() called with non-callable callback")
            return

        with self._lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                Logger.debug(f"Subscribed to '{event_type}'")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if not isinstance(event_type, str):
            return

        with self._lock:
            if callback in self._subscribers.get(event_type, []):
                self._subscribers[event_type].remove(callback)
                Logger.debug(f"Unsubscribed from '{event_type}'")

            if not self._subscribers.get(event_type):
                self._subscribers.pop(event_type, None)

    # ---------------------------------------------------------
    # PUBLISH (synchronous, thread-safe)
    # ---------------------------------------------------------
    def publish(self, event_type: str, data: Any = None) -> None:
        if not isinstance(event_type, str):
            Logger.error("publish() called with non-string event_type")
            return

        callbacks = []
        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))

        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                Logger.error(f"[EventBus] Error in callback '{event_type}': {e}")

    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    def shutdown(self):
        """Stops EventBus (placeholder for future async engines)."""
        Logger.info("Shutting down EventBus...")
        self._running = False
        Logger.info("EventBus shutdown completed.")

    # ---------------------------------------------------------
    # NO-OP API (UI compatibility)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
