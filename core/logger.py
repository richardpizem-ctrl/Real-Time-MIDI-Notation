# Logger

import datetime
import threading


class Logger:
    """
    Stabilizovaný thread‑safe logger:
    - bezpečné timestampy
    - thread‑safe výstup
    - žiadne pády pri nevalidných správach
    - jednotný formát logov
    """

    _lock = threading.Lock()

    @staticmethod
    def _timestamp():
        try:
            return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return "0000-00-00 00:00:00"

    @classmethod
    def info(cls, message):
        with cls._lock:
            try:
                print(f"[INFO] {cls._timestamp()} - {message}")
            except Exception:
                print("[INFO] Logger error: failed to print message")

    @classmethod
    def warning(cls, message):
        with cls._lock:
            try:
                print(f"[WARNING] {cls._timestamp()} - {message}")
            except Exception:
                print("[WARNING] Logger error: failed to print message")

    @classmethod
    def error(cls, message):
        with cls._lock:
            try:
                print(f"[ERROR] {cls._timestamp()} - {message}")
            except Exception:
                print("[ERROR] Logger error: failed to print message")
