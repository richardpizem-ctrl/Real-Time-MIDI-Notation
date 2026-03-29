# MIDI Message Parser

from ..core.logger import Logger


class MessageParser:
    @staticmethod
    def parse(msg):
        """
        Convert raw mido message into a structured dict.
        Stabilizované:
        - ochrana pred None
        - ochrana pred nevalidnými typmi
        - bezpečné čítanie atribútov
        - fallback pri chýbajúcich hodnotách
        """

        if msg is None:
            Logger.warning("MessageParser.parse called with None")
            return None

        # msg musí mať aspoň atribút 'type'
        msg_type = getattr(msg, "type", None)
        if msg_type is None:
            Logger.warning(f"MessageParser: missing msg.type in {msg}")
            return None

        try:
            # -----------------------------
            # NOTE ON
            # -----------------------------
            if msg_type == "note_on":
                return {
                    "type": "note_on",
                    "note": getattr(msg, "note", None),
                    "velocity": getattr(msg, "velocity", 0),
                    "channel": getattr(msg, "channel", 0),
                }

            # -----------------------------
            # NOTE OFF
            # -----------------------------
            elif msg_type == "note_off":
                return {
                    "type": "note_off",
                    "note": getattr(msg, "note", None),
                    "velocity": getattr(msg, "velocity", 0),
                    "channel": getattr(msg, "channel", 0),
                }

            # -----------------------------
            # CONTROL CHANGE
            # -----------------------------
            elif msg_type == "control_change":
                return {
                    "type": "control_change",
                    "control": getattr(msg, "control", None),
                    "value": getattr(msg, "value", None),
                    "channel": getattr(msg, "channel", 0),
                }

            # -----------------------------
            # UNKNOWN MESSAGE TYPE
            # -----------------------------
            else:
                Logger.debug(f"MessageParser: unsupported message type '{msg_type}'")
                return None

        except Exception as e:
            Logger.error(f"MessageParser error: {e}")
            return None
