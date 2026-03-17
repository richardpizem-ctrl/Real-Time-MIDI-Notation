# Status Bar – displays real-time system status

from ..core.logger import Logger

class StatusBar:
    def __init__(self):
        self.tempo = 120
        self.latency_ms = 0
        self.fps = 0
        self.last_note = None
        self.midi_status = "Disconnected"

        Logger.info("StatusBar initialized.")

    def update(self, tempo=None, latency=None, fps=None, last_note=None, midi_status=None):
        """Updates status bar values."""
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

    def display(self):
        """Temporary console output for debugging."""
        try:
            text = (
                f"TEMPO: {self.tempo} BPM | "
                f"LATENCY: {self.latency_ms} ms | "
                f"FPS: {self.fps} | "
                f"LAST NOTE: {self.last_note} | "
                f"MIDI: {self.midi_status}"
            )

            print(text)
            Logger.info(f"StatusBar: {text}")

        except Exception as e:
            Logger.error(f"StatusBar display error: {e}")

