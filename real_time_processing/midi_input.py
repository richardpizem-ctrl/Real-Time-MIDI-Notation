"""Polling compatibility adapter using the canonical message parser."""
import mido
from midi_input.message_parser import MessageParser
class MidiInput:
    def __init__(self, device_name=None):
        self.port=None
        self.error=None
        try:
            names=mido.get_input_names()
            selected=device_name or (names[0] if names else None)
            if selected is not None and selected in names:
                self.port=mido.open_input(selected)
        except Exception as error:
            self.error=str(error)
    def poll_events(self):
        if self.port is None:return []
        try:
            return [event for message in self.port.iter_pending() if (event:=MessageParser.parse(message)) is not None]
        except Exception as error:
            self.error=str(error)
            self.close()
            return []
    def close(self):
        if self.port is not None:
            self.port.close()
            self.port=None
