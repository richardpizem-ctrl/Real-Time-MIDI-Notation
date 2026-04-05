# Logger – stabilný thread‑safe logger pre celý projekt

import datetime
import threading


class Logger:
    """
    Stabilizovaný thread‑safe logger:
    - bezpečné timestampy
    - thread‑safe výstup
    - jednotný formát logov
    - ochrana proti nevalidným správam
    - podpora INFO / WARNING / ERROR / DEBUG
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
