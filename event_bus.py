# =========================================================
# EventBus v2.0.0 – Stabilný, bezpečný, thread-safe event systém
# =========================================================

import threading
from collections import defaultdict
from typing import Callable, Any, Dict, List

from core.logger import Logger


class EventBus:
    """
    EventBus (v2.0.0)
    -----------------
    Stabilný, bezpečný, thread-safe event router pre celý projekt.

    Funkcie:
        - subscribe(event_type, callback)
        - unsubscribe(event_type, callback)
        - publish(event_type, data)
        - publish_async(event_type, data)

    Vlastnosti:
        - žiadne výnimky nesmú preraziť
        - callbacky sa volajú mimo locku (bez deadlockov)
        - ochrana pred nevalidnými event typmi a callbackmi
        - pripravené pre v3 (AI/TIMELINE event hooks)
    """

    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()
        Logger.info("EventBus initialized (v2.0.0).")

    # ---------------------------------------------------------
    # VALIDÁCIA
    # ---------------------------------------------------------
    def _validate_event_type(self, event_type: str) -> bool:
        if not isinstance(event_type, str) or not event_type.strip():
            Logger.error("EventBus: invalid event_type")
            return False
        return True

    def _validate_callback(self, callback) -> bool:
        if not callable(callback):
            Logger.error("EventBus: callback is not callable")
            return False
        return True

    # ---------------------------------------------------------
    # SUBSCRIBE
    # ---------------------------------------------------------
    def subscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Zaregistruje callback pre daný typ udalosti."""
        if not self._validate_event_type(event_type):
            return
        if not self._validate_callback(callback):
            return

        with self._lock:
            if callback not in self._subscribers[event_type]:
                self._subscribers[event_type].append(callback)
                Logger.debug(f"Subscribed to event '{event_type}'")

    # ---------------------------------------------------------
    # UNSUBSCRIBE
    # ---------------------------------------------------------
    def unsubscribe(self, event_type: str, callback: Callable[[Any], None]) -> None:
        """Odstráni callback z daného typu udalosti."""
        if not self._validate_event_type(event_type):
            return
        if not self._validate_callback(callback):
            return

        with self._lock:
            if callback in self._subscribers[event_type]:
                self._subscribers[event_type].remove(callback)
                Logger.debug(f"Unsubscribed from event '{event_type}'")

            if not self._subscribers[event_type]:
                del self._subscribers[event_type]

    # ---------------------------------------------------------
    # SYNCHRÓNNE PUBLIKOVANIE
    # ---------------------------------------------------------
    def publish(self, event_type: str, data: Any = None) -> None:
        """Synchronne odošle udalosť všetkým odberateľom."""
        if not self._validate_event_type(event_type):
            return

        with self._lock:
            callbacks = list(self._subscribers.get(event_type, []))

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
        if not self._validate_event_type(event_type):
            return

        thread = threading.Thread(
            target=self.publish,
            args=(event_type, data),
            daemon=True
        )
        thread.start()

        Logger.debug(f"Async publish scheduled for event '{event_type}'")

    # ---------------------------------------------------------
    # NO-OP API (UI kompatibilita)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
