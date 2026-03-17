# MIDI Listener

import threading
import mido
from .message_parser import MessageParser
from ..core.logger import Logger

class MIDIListener:
    def __init__(self, event_bus, device_name=None):
        self.event_bus = event_bus
        self.device_name = device_name
        self.running = False
        self.thread = None

    def start(self):
        """Start listening to MIDI input."""
        if self.running:
            Logger.warning("MIDIListener is already running.")
            return

        self.running = True
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()
        Logger.info("MIDIListener started.")

    def stop(self):
        """Stop listening."""
        self.running = False
        Logger.info("MIDIListener stopped.")

    def _listen_loop(self):
        """Internal loop for receiving MIDI messages."""
        try:
            with mido.open_input(self.device_name) as port:
                Logger.info(f"Listening on MIDI device: {port.name}")

                for msg in port:
                    if not self.running:
                        break

                    parsed = MessageParser.parse(msg)
                    if parsed:
                        self.event_bus.publish("midi_event", parsed)

        except Exception as e:
            Logger.error(f"MIDIListener error: {e}")

