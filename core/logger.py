# =========================================================
# Logger v4.1.0
# Stabilný, thread-safe logger pre celý systém
# =========================================================

import datetime
import threading


class Logger:
    """
    Logger v4.1.0:
    - thread-safe
    - stabilný
    - bez async threadov
    - bez AI routingu
    - bez EventBus routingu
    - nikdy nespadne
    """

    _lock = threading.Lock()

    # ---------------------------------------------------------
    # TIMESTAMP
    # ---------------------------------------------------------
    @staticmethod
    def _timestamp():
        try:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "0000-00-00 00:00:00"

    # ---------------------------------------------------------
    # INTERNAL SAFE PRINT
    # ---------------------------------------------------------
    @classmethod
    def _safe_print(cls, level: str, message: str):
        """Bezpečný výpis logu – nikdy nespadne."""
        with cls._lock:
            try:
                msg = str(message)
            except Exception:
                msg = "<invalid log message>"

            # Ochrana pred extrémne dlhými správami
            if len(msg) > 5000:
                msg = msg[:5000] + "... [truncated]"

            try:
                print(f"[{level}] {cls._timestamp()} - {msg}")
            except Exception:
                pass

    # ---------------------------------------------------------
    # PUBLIC LOG METHODS
    # ---------------------------------------------------------
    @classmethod
    def debug(cls, message):
        cls._safe_print("DEBUG", message)

    @classmethod
    def info(cls, message):
        cls._safe_print("INFO", message)

    @classmethod
    def warning(cls, message):
        cls._safe_print("WARNING", message)

    @classmethod
    def error(cls, message):
        cls._safe_print("ERROR", message)

    @classmethod
    def critical(cls, message):
        cls._safe_print("CRITICAL", message)

    # ---------------------------------------------------------
    # NO-OP API (UI compatibility)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
