# =========================================================
# Logger v2.0.0
# Stabilný, thread-safe logger pre celý MIDI Engine
# =========================================================

import datetime
import threading


class Logger:
    """
    Stabilizovaný thread‑safe logger (v2.0.0):
    - bezpečné timestampy
    - thread‑safe výstup
    - jednotný formát logov
    - ochrana proti nevalidným správam
    - ochrana proti extrémne dlhým správam
    - podpora INFO / WARNING / ERROR / DEBUG
    - fail‑safe: nikdy nespadne
    """

    _lock = threading.Lock()

    # ---------------------------------------------------------
    # TIMESTAMP
    # ---------------------------------------------------------
    @staticmethod
    def _timestamp():
        """Bezpečné generovanie timestampu."""
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
                # Fallback – ak print() zlyhá, už nič nerobíme
                pass

    # ---------------------------------------------------------
    # PUBLIC LOG METHODS
    # ---------------------------------------------------------
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
    def debug(cls, message):
        cls._safe_print("DEBUG", message)

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
