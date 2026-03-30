# Event bus – centrálne smerovanie udalostí v aplikácii

import threading
from collections import defaultdict
from typing import Callable, Any, Dict, List


class EventBus:
    """
    Jednoduchý, ale rozšíriteľný event bus pre celý projekt.

    Podporuje:
    - subscribe(event_type, callback)
    - unsubscribe(event_type, callback)
    - publish(event_type, data)
    - publish_async(event_type, data)
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()

    # ---------------------------------------------------------
    # REGISTRÁCIA CALLBACKOV
    # ---------------------------------------------------------
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Zaregistruje callback pre daný typ udalosti."""
        with self._lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Odstráni callback z daného typu udalosti."""
        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)

            # Ak už nemá žiadnych odberateľov, odstránime celý záznam
            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    # ---------------------------------------------------------
    # SYNCHRÓNNE PUBLIKOVANIE
    # ---------------------------------------------------------
    def publish(self, event_type: str, data: Any = None) -> None:
        """Synchronne odošle udalosť všetkým odberateľom."""
        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))

        for callback in callbacks:
            try:
                callback(data)
            except Exception as e:
                print(f"[EventBus] Error in callback for '{event_type}': {e}")

    # ---------------------------------------------------------
    # ASYNCHRÓNNE PUBLIKOVANIE
    # ---------------------------------------------------------
    def publish_async(self, event_type: str, data: Any = None) -> None:
        """Asynchrónne odošle udalosť v samostatnom vlákne."""
        thread = threading.Thread(
            target=self.publish,
            args=(event_type, data),
            daemon=True
        )
        thread.start()

