# Event bus – centrálne smerovanie udalostí v aplikácii

import threading
from collections import defaultdict
from typing import Callable, Any, Dict, List
from .logger import Logger


class EventBus:
    """
    Stabilný, thread-safe event bus pre celý projekt.

    Funkcie:
    - subscribe(event_type, callback)
    - unsubscribe(event_type, callback)
    - publish(event_type, data)
    - publish_async(event_type, data)

    Vlastnosti:
    - bezpečné volanie callbackov
    - žiadne deadlocky (callbacky sa volajú mimo locku)
    - ochrana proti výnimkám v callbackoch
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()
        Logger.info("EventBus initialized.")

    # ---------------------------------------------------------
    # REGISTRÁCIA CALLBACKOV
    # ---------------------------------------------------------
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Zaregistruje callback pre daný typ udalosti."""
        if not isinstance(event_type, str):
            raise ValueError("event_type must be a string")

        if not callable(callback):
            raise ValueError("callback must be callable")

        with self._lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                Logger.debug(f"Subscribed to event '{event_type}': {callback}")

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Odstráni callback z daného typu udalosti."""
        if not isinstance(event_type, str):
            return

        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                Logger.debug(f"Unsubscribed from event '{event_type}': {callback}")

            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    # ---------------------------------------------------------
    # SYNCHRÓNNE PUBLIKOVANIE
    # ---------------------------------------------------------
    def publish(self, event_type: str, data: Any = None) -> None:
        """Synchronne odošle udalosť všetkým odberateľom."""
        if not isinstance(event_type, str):
            Logger.error("publish() called with non-string event_type")
            return

        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))

        Logger.debug(f"Publishing event '{event_type}' to {len(callbacks)} subscribers.")

        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                Logger.error(f"[EventBus] Error in callback for '{event_type}': {e}")

    # ---------------------------------------------------------
    # ASYNCHRÓNNE PUBLIKOVANIE
    # ---------------------------------------------------------
    def publish_async(self, event_type: str, data: Any = None) -> None:
        """Asynchrónne odošle udalosť v samostatnom vlákne."""
        if not isinstance(event_type, str):
            Logger.error("publish_async() called with non-string event_type")
            return

        thread = threading.Thread(
            target=self.publish,
            args=(event_type, data),
            daemon=True
        )
        thread.start()

        Logger.debug(f"Async publish scheduled for event '{event_type}'.")
