# Debug Panel – shows raw MIDI events and internal pipeline data

from ..core.logger import Logger

class DebugPanel:
    def __init__(self):
        self.enabled = True
        Logger.info("DebugPanel initialized.")

    def log_midi_event(self, event):
        """Display raw MIDI event."""
        if not self.enabled:
            return

        try:
            print(f"[MIDI EVENT] {event}")
            Logger.info(f"Debug MIDI event: {event}")
        except Exception as e:
            Logger.error(f"DebugPanel MIDI error: {e}")

    def log_pipeline(self, stage, data):
        """Display pipeline stage output."""
        if not self.enabled:
            return

        try:
            print(f"[PIPELINE] {stage}: {data}")
            Logger.info(f"Debug pipeline {stage}: {data}")
        except Exception as e:
            Logger.error(f"DebugPanel pipeline error: {e}")

    def log_error(self, message):
        """Display error messages."""
        try:
            print(f"[ERROR] {message}")
            Logger.error(f"DebugPanel error: {message}")
        except Exception as e:
            Logger.error(f"DebugPanel logging failure: {e}")

