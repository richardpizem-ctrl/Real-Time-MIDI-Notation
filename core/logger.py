# =========================================================
# Logger v4.0.0-ready
# High-performance, async, thread-safe logging system
# =========================================================

import datetime
import threading
from collections import deque
import json


class Logger:
    """
    Logger v4-ready:
    - async logging (dispatcher thread)
    - deque-based log queue
    - log level filtering
    - high-precision timestamps
    - optional JSON structured logs
    - AI / EventBus routing hooks
    - fail-safe (never crashes)
    """

    _lock = threading.Lock()
    _queue = deque()
    _running = True
    _log_level = "DEBUG"  # DEBUG / INFO / WARNING / ERROR / CRITICAL
    _use_json = False

    ai_engine = None
    event_bus = None

    # Dispatcher thread
    _dispatcher = threading.Thread(
        target=lambda: Logger._dispatch_loop(),
        daemon=True
    )
    _dispatcher.start()

    # ---------------------------------------------------------
    # TIMESTAMP (high precision)
    # ---------------------------------------------------------
    @staticmethod
    def _timestamp():
        try:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        except Exception:
            return "0000-00-00 00:00:00.000"

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    @classmethod
    def set_level(cls, level: str):
        cls._log_level = level.upper()

    @classmethod
    def enable_json(cls, enabled: bool):
        cls._use_json = enabled

    @classmethod
    def attach_ai_engine(cls, ai_engine):
        cls.ai_engine = ai_engine

    @classmethod
    def attach_event_bus(cls, event_bus):
        cls.event_bus = event_bus

    # ---------------------------------------------------------
    # LOG METHODS
    # ---------------------------------------------------------
    @classmethod
    def debug(cls, message):
        cls._enqueue("DEBUG", message)

    @classmethod
    def info(cls, message):
        cls._enqueue("INFO", message)

    @classmethod
    def warning(cls, message):
        cls._enqueue("WARNING", message)

    @classmethod
    def error(cls, message):
        cls._enqueue("ERROR", message)

    @classmethod
    def critical(cls, message):
        cls._enqueue("CRITICAL", message)

    # ---------------------------------------------------------
    # INTERNAL QUEUEING
    # ---------------------------------------------------------
    @classmethod
    def _enqueue(cls, level: str, message: str):
        try:
            with cls._lock:
                cls._queue.append((level, message))
        except Exception:
            pass  # fail-safe

    # ---------------------------------------------------------
    # DISPATCH LOOP
    # ---------------------------------------------------------
    @classmethod
    def _dispatch_loop(cls):
        while cls._running:
            if not cls._queue:
                continue

            with cls._lock:
                level, message = cls._queue.popleft()

            # Level filtering
            if not cls._allow_level(level):
                continue

            # Format log
            formatted = cls._format(level, message)

            # Console output
            try:
                print(formatted)
            except Exception:
                pass

            # AI routing
            if cls.ai_engine and hasattr(cls.ai_engine, "on_log"):
                try:
                    cls.ai_engine.on_log(level, message)
                except Exception:
                    pass

            # EventBus routing
            if cls.event_bus:
                try:
                    cls.event_bus.publish("system.log", {
                        "level": level,
                        "message": message,
                        "timestamp": cls._timestamp()
                    })
                except Exception:
                    pass

    # ---------------------------------------------------------
    # LEVEL CHECK
    # ---------------------------------------------------------
    @classmethod
    def _allow_level(cls, level: str) -> bool:
        order = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        return order.index(level) >= order.index(cls._log_level)

    # ---------------------------------------------------------
    # FORMATTER
    # ---------------------------------------------------------
    @classmethod
    def _format(cls, level: str, message: str) -> str:
        timestamp = cls._timestamp()

        if cls._use_json:
            return json.dumps({
                "timestamp": timestamp,
                "level": level,
                "message": str(message)
            })

        return f"[{level}] {timestamp} - {message}"

    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    @classmethod
    def shutdown(cls):
        cls._running = False
        try:
            cls._dispatcher.join(timeout=1.0)
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
