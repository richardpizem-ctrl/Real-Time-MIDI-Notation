# =========================================================
# EventBus v4.0.0-ready
# High-performance, async, burst-safe event router
# =========================================================

import threading
import time
from collections import defaultdict, deque
from typing import Callable, Any, Dict, List, Tuple
from .logger import Logger


class EventBus:
    """
    EventBus v4-ready:
    - deque-based event queue
    - dispatcher thread
    - async + non-blocking publish
    - event priorities
    - batching
    - AI event channel support
    - safe shutdown
    """

    def __init__(self):
        Logger.info("Initializing EventBus (v4-ready)...")

        # Subscribers
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)

        # Event queue: (priority, event_type, data)
        self._queue: deque[Tuple[int, str, Any]] = deque()

        # Threading
        self._lock = threading.Lock()
        self._running = True

        # Dispatcher thread
        self._dispatcher = threading.Thread(
            target=self._dispatch_loop,
            daemon=True
        )
        self._dispatcher.start()

        Logger.info("EventBus initialized (v4-ready).")

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
                Logger.debug(f"Subscribed to '{event_type}': {callback}")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        if not isinstance(event_type, str):
            return

        with self._lock:
            if callback in self._subscribers.get(event_type, []):
                self._subscribers[event_type].remove(callback)
                Logger.debug(f"Unsubscribed from '{event_type}': {callback}")

            if not self._subscribers.get(event_type):
                self._subscribers.pop(event_type, None)

    # ---------------------------------------------------------
    # PUBLISH (non-blocking)
    # ---------------------------------------------------------
    def publish(self, event_type: str, data: Any = None, priority: int = 5) -> None:
        """
        Non-blocking publish:
        - priority: 1 = highest, 10 = lowest
        """
        if not isinstance(event_type, str):
            Logger.error("publish() called with non-string event_type")
            return

        with self._lock:
            self._queue.append((priority, event_type, data))

    # ---------------------------------------------------------
    # ASYNC PUBLISH
    # ---------------------------------------------------------
    def publish_async(self, event_type: str, data: Any = None, priority: int = 5) -> None:
        threading.Thread(
            target=self.publish,
            args=(event_type, data, priority),
            daemon=True
        ).start()

    # ---------------------------------------------------------
    # DISPATCH LOOP (v4)
    # ---------------------------------------------------------
    def _dispatch_loop(self):
        """High-performance dispatcher loop."""
        while self._running:
            if not self._queue:
                time.sleep(0.0005)
                continue

            # Batch processing
            batch = []
            with self._lock:
                while self._queue and len(batch) < 32:
                    batch.append(self._queue.popleft())

            # Sort by priority
            batch.sort(key=lambda x: x[0])

            # Dispatch events
            for _, event_type, data in batch:
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
        """Stops dispatcher thread safely."""
        Logger.info("Shutting down EventBus...")
        self._running = False
        self._dispatcher.join(timeout=1.0)
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
