"""
error_handler.py – Centralized and safe error handling for real-time processing (FÁZA 4)

Poskytuje:
- jednotné logovanie
- bezpečné volanie funkcií
- dekorátor pre real-time pipeline
- ochranu pred zlyhaním Loggera
- konzistentné návratové hodnoty
"""

from ..core.logger import Logger
from typing import Any, Callable, Optional


class ErrorHandler:
    """
    Centralized error handler for real-time processing.
    Provides safe wrappers and unified logging for exceptions.
    """

    @staticmethod
    def handle(error: Exception,
               context: Optional[str] = None,
               raise_error: bool = False) -> None:
        """
        Handle an exception with optional context.
        If raise_error=True → re-raises after logging.
        """
        try:
            ctx = f" | context={context}" if context else ""
            Logger.error(f"[ErrorHandler] {type(error).__name__}: {error}{ctx}")
        except Exception:
            # Fallback if Logger itself fails
            print(f"[ErrorHandler] {type(error).__name__}: {error} (logging failed)")

        if raise_error:
            raise error

    @staticmethod
    def safe_call(func: Callable,
                  *args,
                  context: Optional[str] = None,
                  raise_error: bool = False,
                  **kwargs) -> Any:
        """
        Safely call a function.
        On exception:
            - logs via ErrorHandler
            - returns None (unless raise_error=True)
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle(e, context=context, raise_error=raise_error)
            return None


def safe_execute(func: Callable) -> Callable:
    """
    Decorator for safe execution of functions in real-time pipeline.
    Logs all exceptions via ErrorHandler and prevents hard crashes.
    """

    def wrapper(*args, **kwargs):
        context = kwargs.pop("error_context", None)
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle(e, context=context, raise_error=False)
            return None

    return wrapper
