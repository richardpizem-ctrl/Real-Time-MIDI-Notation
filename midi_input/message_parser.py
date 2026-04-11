# MIDI Message Parser

import time
from ..core.logger import Logger


class MessageParser:
    @staticmethod
    def parse(msg):
        """
        Convert raw mido message into a structured dict.

        Stabilizované (Fáza 4):
        - ochrana pred None
        - ochrana pred nevalidnými typmi
        - bezpečné čítanie atribútov
        - fallback pri chýbajúcich hodnotách
        - clampovanie kanála
        - clampovanie velocity
        - pridanie timestampu
        """

        if msg is None:
            Logger.warning("MessageParser.parse called with None")
            return None

        # msg musí mať aspoň atribút 'type'
        msg_type = getattr(msg, "type", None)
        if not isinstance(msg_type, str):
            Logger.warning(f"MessageParser: missing or invalid msg.type in {msg}")
            return None

        try:
            # Normalizácia kanála (0–15)
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

                try:
                    note = int(note) if note is not None else None
                except Exception:
                    note = None

                try:
                    velocity = int(velocity)
                except Exception:
                    velocity = 0

                velocity = max(0, min(127, velocity))

                return {
                    "type": "note_on",
                    "note": note,
                    "velocity": velocity,
                    "channel": channel,
                    "timestamp": timestamp,
                }

            # -----------------------------
            # NOTE OFF
            # -----------------------------
            elif msg_type == "note_off":
                note = getattr(msg, "note", None)
                velocity = getattr(msg, "velocity", 0)

                try:
                    note = int(note) if note is not None else None
                except Exception:
                    note = None

                try:
                    velocity = int(velocity)
                except Exception:
                    velocity = 0

                velocity = max(0, min(127, velocity))

                return {
                    "type": "note_off",
                    "note": note,
                    "velocity": velocity,
                    "channel": channel,
                    "timestamp": timestamp,
                }

            # -----------------------------
            # CONTROL CHANGE
            # -----------------------------
            elif msg_type == "control_change":
                control = getattr(msg, "control", None)
                value = getattr(msg, "value", None)

                try:
                    control = int(control) if control is not None else None
                except Exception:
                    control = None

                try:
                    value = int(value) if value is not None else None
                except Exception:
                    value = None

                if value is not None:
                    value = max(0, min(127, value))

                return {
                    "type": "control_change",
                    "control": control,
                    "value": value,
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

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
