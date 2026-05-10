# =========================================================
# DebugPanel v4.0.0
# Stable, safe and real‑time friendly debug logger
# =========================================================

from typing import Any
from ..core.logger import Logger


class DebugPanel:
    """
    DebugPanel (v4.0.0)
    -------------------
    Safe debug logging for MIDI events, pipeline stages and errors.

    Features:
        - real‑time safe
        - no exceptions
        - clean English API
        - safe object formatting
        - toggleable debug mode
        - UIManager compatible
    """

    def __init__(self, enabled: bool = True, print_enabled: bool = True) -> None:
        self.enabled = bool(enabled)
        self.print_enabled = bool(print_enabled)

        if self.enabled:
            Logger.info("DebugPanel initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self) -> bool:
        """Toggle debug mode and return new state."""
        self.enabled = not self.enabled
        try:
            Logger.info(f"DebugPanel toggled: {self.enabled}")
        except Exception:
            pass
        return self.enabled

    # ---------------------------------------------------------
    # MIDI EVENT LOGGING
    # ---------------------------------------------------------
    def log_midi_event(self, event: Any) -> None:
        """Log a MIDI event."""
        if not self.enabled:
            return

        try:
            safe_event = self._safe_format(event)

            if self.print_enabled:
                print(f"[MIDI EVENT] {safe_event}")

            Logger.info(f"MIDI event: {safe_event}")

        except Exception:
            try:
                Logger.error("DebugPanel MIDI logging failure")
            except Exception:
                pass

    # ---------------------------------------------------------
    # PIPELINE LOGGING
    # ---------------------------------------------------------
    def log_pipeline(self, stage: str, data: Any) -> None:
        """Log a pipeline stage."""
        if not self.enabled:
            return

        try:
            safe_data = self._safe_format(data)

            if self.print_enabled:
                print(f"[PIPELINE] {stage}: {safe_data}")

            Logger.info(f"Pipeline {stage}: {safe_data}")

        except Exception:
            try:
                Logger.error("DebugPanel pipeline logging failure")
            except Exception:
                pass

    # ---------------------------------------------------------
    # ERROR LOGGING
    # ---------------------------------------------------------
    def log_error(self, message: Any) -> None:
        """Log an error message."""
        try:
            safe_msg = self._safe_format(message)

            if self.print_enabled:
                print(f"[ERROR] {safe_msg}")

            Logger.error(f"Error: {safe_msg}")

        except Exception:
            try:
                Logger.error("DebugPanel error logging failure")
            except Exception:
                pass

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj: Any) -> str:
        """Safely convert object to string."""
        try:
            return str(obj)
        except Exception:
            return "<unprintable object>"
