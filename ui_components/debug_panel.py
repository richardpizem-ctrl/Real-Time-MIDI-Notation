# Debug Panel – shows raw MIDI events and internal pipeline data

from ..core.logger import Logger

class DebugPanel:
    def __init__(self, enabled=True, print_enabled=True):
        """
        enabled = či sa debug panel používa
        print_enabled = či sa majú vypisovať print() do konzoly
        """
        self.enabled = enabled
        self.print_enabled = print_enabled

        Logger.info("DebugPanel initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self):
        self.enabled = not self.enabled
        Logger.info(f"DebugPanel toggled: {self.enabled}")

    # ---------------------------------------------------------
    # MIDI EVENT LOGGING
    # ---------------------------------------------------------
    def log_midi_event(self, event):
        """Display raw MIDI event."""
        if not self.enabled:
            return

        try:
            safe_event = self._safe_format(event)

            if self.print_enabled:
                print(f"[MIDI EVENT] {safe_event}")

            Logger.info(f"Debug MIDI event: {safe_event}")

        except Exception as e:
            Logger.error(f"DebugPanel MIDI error: {e}")

    # ---------------------------------------------------------
    # PIPELINE LOGGING
    # ---------------------------------------------------------
    def log_pipeline(self, stage, data):
        """Display pipeline stage output."""
        if not self.enabled:
            return

        try:
            safe_data = self._safe_format(data)

            if self.print_enabled:
                print(f"[PIPELINE] {stage}: {safe_data}")

            Logger.info(f"Debug pipeline {stage}: {safe_data}")

        except Exception as e:
            Logger.error(f"DebugPanel pipeline error: {e}")

    # ---------------------------------------------------------
    # ERROR LOGGING
    # ---------------------------------------------------------
    def log_error(self, message):
        """Display error messages."""
        try:
            if self.print_enabled:
                print(f"[ERROR] {message}")

            Logger.error(f"DebugPanel error: {message}")

        except Exception as e:
            Logger.error(f"DebugPanel logging failure: {e}")

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe_format(self, obj):
        """
        Bezpečne prevedie objekt na string,
        aby Logger nespadol pri ne-serializovateľných dátach.
        """
        try:
            return str(obj)
        except Exception:
            return "<unprintable object>"
