# error_handler.py – Centralized error handling for real-time processing

from ..core.logger import Logger


class ErrorHandler:
    """
    Centralized error handler for real-time processing.
    Provides safe wrappers and unified logging for exceptions.
    """

    @staticmethod
    def handle(error, context=None, raise_error=False):
        """
        Handle an exception with optional context.
        If raise_error is True, re-raises after logging.
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
    def safe_call(func, *args, context=None, raise_error=False, **kwargs):
        """
        Call a function safely. On exception, logs via ErrorHandler
        and returns None (or re-raises if raise_error=True).
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            ErrorHandler.handle(e, context=context, raise_error=raise_error)
            return None


def safe_execute(func):
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
