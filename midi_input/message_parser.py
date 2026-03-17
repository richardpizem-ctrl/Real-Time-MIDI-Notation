# MIDI Message Parser

from ..core.logger import Logger

class MessageParser:
    @staticmethod
    def parse(msg):
        """Convert raw mido message into a structured dict."""
        try:
            if msg.type == "note_on":
                return {
                    "type": "note_on",
                    "note": msg.note,
                    "velocity": msg.velocity,
                    "channel": msg.channel
                }

            elif msg.type == "note_off":
                return {
                    "type": "note_off",
                    "note": msg.note,
                    "velocity": msg.velocity,
                    "channel": msg.channel
                }

            elif msg.type == "control_change":
                return {
                    "type": "control_change",
                    "control": msg.control,
                    "value": msg.value,
                    "channel": msg.channel
                }

            else:
                # Neznáme alebo nepodporované správy ignorujeme
                return None

        except Exception as e:
            Logger.error(f"MessageParser error: {e}")
            return None

