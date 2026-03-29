from ..core.logger import Logger

class StatusBar:
    def __init__(self, enabled=True, print_enabled=True):
        self.enabled = enabled
        self.print_enabled = print_enabled

        self.tempo = 120
        self.latency_ms = 0
        self.fps = 0
        self.last_note = None
        self.midi_status = "Disconnected"

        Logger.info("StatusBar initialized.")

    # ---------------------------------------------------------
    # ENABLE / DISABLE
    # ---------------------------------------------------------
    def toggle(self):
        self.enabled = not self.enabled
        Logger.info(f"StatusBar toggled: {self.enabled}")

    # ---------------------------------------------------------
    # UPDATE VALUES
    # ---------------------------------------------------------
    def update(self, tempo=None, latency=None, fps=None, last_note=None, midi_status=None):
        if not self.enabled:
            return

        try:
            if tempo is not None:
                self.tempo = tempo

            if latency is not None:
                self.latency_ms = latency

            if fps is not None:
                self.fps = fps

            if last_note is not None:
                self.last_note = last_note

            if midi_status is not None:
                self.midi_status = midi_status

            self.display()

        except Exception as e:
            Logger.error(f"StatusBar update error: {e}")

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------
    def display(self):
        if not self.enabled:
            return

        try:
            text = (
                f"TEMPO: {self._safe(self.tempo)} BPM | "
                f"LATENCY: {self._safe(self.latency_ms)} ms | "
                f"FPS: {self._safe(self.fps)} | "
                f"LAST NOTE: {self._safe(self.last_note)} | "
                f"MIDI: {self._safe(self.midi_status)}"
            )

            if self.print_enabled:
                print(text)

            Logger.info(f"StatusBar: {text}")

        except Exception as e:
            Logger.error(f"StatusBar display error: {e}")

    # ---------------------------------------------------------
    # SAFE FORMATTER
    # ---------------------------------------------------------
    def _safe(self, value):
        try:
            return str(value)
        except Exception:
            return "<unprintable>"
