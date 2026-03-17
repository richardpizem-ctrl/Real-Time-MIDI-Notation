# Logger

import datetime
import threading

class Logger:
    _lock = threading.Lock()

    @staticmethod
    def _timestamp():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @classmethod
    def info(cls, message):
        with cls._lock:
            print(f"[INFO] {cls._timestamp()} - {message}")

    @classmethod
    def warning(cls, message):
        with cls._lock:
            print(f"[WARNING] {cls._timestamp()} - {message}")

    @classmethod
    def error(cls, message):
        with cls._lock:
            print(f"[ERROR] {cls._timestamp()} - {message}")

