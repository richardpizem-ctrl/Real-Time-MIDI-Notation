# MIDI Event Router

from ..core.logger import Logger


class EventRouter:
    def __init__(self, event_bus, piano_roll_ui=None):
        """
        event_bus      = centrálny EventBus
        piano_roll_ui  = inštancia PianoRollUI (voliteľné)
        """
        self.event_bus = event_bus
        self.piano_roll = piano_roll_ui

        Logger.info("EventRouter initialized.")

    # ---------------------------------------------------------
    # ROUTING MIDI EVENTOV
    # ---------------------------------------------------------
    def route(self, midi_event):
        """
        Route parsed MIDI event to the correct event bus channel.
        midi_event je dict:
        {
            "type": "note_on" / "note_off" / "control_change",
            "note": int,
            "velocity": int,
            "timestamp": float
        }
        """
        try:
            event_type = midi_event.get("type")

            # -------------------------
            # NOTE ON / NOTE OFF
            # -------------------------
            if event_type in ("note_on", "note_off"):
                # Posielame do EventBus
                self.event_bus.publish("note_event", midi_event)

                # 🔥 Prepojenie na Piano Roll UI
                if self.piano_roll:
                    if event_type == "note_on" and midi_event.get("velocity", 0) > 0:
                        self.piano_roll.highlight_key(
                            midi_event["note"],
                            color=(255, 80, 80)
                        )
                    else:
                        self.piano_roll.unhighlight_key(midi_event["note"])

            # -------------------------
            # CONTROL CHANGE
            # -------------------------
            elif event_type == "control_change":
                self.event_bus.publish("control_event", midi_event)

            # -------------------------
            # UNKNOWN
            # -------------------------
            else:
                Logger.warning(f"Unknown MIDI event type: {event_type}")

        except Exception as e:
            Logger.error(f"EventRouter error: {e}")
