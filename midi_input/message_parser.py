# MIDI Message Parser

import time
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
        - pridanie timestampu
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
            # Normalizácia kanála (Mido používa 0–15, projekt používa 1–16)
            channel = getattr(msg, "channel", 0)
            try:
                channel = int(channel)
            except Exception:
                channel = 0
            channel = max(0, min(15, channel))

            timestamp = time.time()

            # -----------------------------
            # NOTE ON
            # -----------------------------
            if msg_type == "note_on":
                note = getattr(msg, "note", None)
                velocity = getattr(msg, "velocity", 0)

                return {
                    "type": "note_on",
                    "note": int(note) if note is not None else None,
                    "velocity": int(velocity),
                    "channel": channel,
                    "timestamp": timestamp,
                }

            # -----------------------------
            # NOTE OFF
            # -----------------------------
            elif msg_type == "note_off":
                note = getattr(msg, "note", None)
                velocity = getattr(msg, "velocity", 0)

                return {
                    "type": "note_off",
                    "note": int(note) if note is not None else None,
                    "velocity": int(velocity),
                    "channel": channel,
                    "timestamp": timestamp,
                }

            # -----------------------------
            # CONTROL CHANGE
            # -----------------------------
            elif msg_type == "control_change":
                control = getattr(msg, "control", None)
                value = getattr(msg, "value", None)

                return {
                    "type": "control_change",
                    "control": int(control) if control is not None else None,
                    "value": int(value) if value is not None else None,
                    "channel": channel,
                    "timestamp": timestamp,
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
