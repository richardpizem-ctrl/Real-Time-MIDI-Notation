# =========================================================
# ErrorHandler v2.0.0
# Stabilné a bezpečné centrálne spracovanie chýb
# pre Real-Time-MIDI-Notation
# =========================================================

from ..core.logger import Logger
from typing import Any, Callable, Optional


class ErrorHandler:
    """
    ErrorHandler (v2.0.0):
    - jednotné logovanie
    - bezpečné volanie funkcií
    - ochrana pred zlyhaním Loggera
    - konzistentné návratové hodnoty
    - pripravené na real-time pipeline v3
    """

    @staticmethod
    def handle(
        error: Exception,
        context: Optional[str] = None,
        raise_error: bool = False
    ) -> None:
        """
        Bezpečné spracovanie výnimky.
        Ak raise_error=True → po zalogovaní re-raise.
        """
        try:
            ctx = f" | context={context}" if context else ""
            Logger.error(f"[ErrorHandler] {type(error).__name__}: {error}{ctx}")
        except Exception:
            # Fallback ak Logger zlyhá
            print(f"[ErrorHandler] {type(error).__name__}: {error} (logging failed)")

        if raise_error:
            raise error

    @staticmethod
    def safe_call(
        func: Callable,
        *args,
        context: Optional[str] = None,
        raise_error: bool = False,
        **kwargs
    ) -> Any:
        """
        Bezpečné volanie funkcie.
        Pri chybe:
            - zaloguje
            - vráti None (ak raise_error=False)
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle(e, context=context, raise_error=raise_error)
            return None


def safe_execute(func: Callable) -> Callable:
    """
    Dekorátor pre bezpečné vykonanie funkcie v real-time pipeline.
    Zachytí všetky výnimky a zabráni pádu systému.
    """

    def wrapper(*args, **kwargs):
        context = kwargs.pop("error_context", None)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle(e, context=context, raise_error=False)
            return None

    return wrapper
