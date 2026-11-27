"""Mido normalization; live timestamps use monotonic seconds, never MIDI ticks."""
import time
import mido
class MessageParser:
    TYPES = {'note_on','note_off','control_change','pitchwheel','program_change','aftertouch','polytouch'}
    @staticmethod
    def parse(message, timestamp=None):
        if not isinstance(message, mido.Message) or message.type not in MessageParser.TYPES:
            return None
        event = message.dict()
        event['time'] = time.monotonic() if timestamp is None else float(timestamp)
        if event['type'] == 'note_on' and event['velocity'] == 0:
            event['type'] = 'note_off'
        return event
