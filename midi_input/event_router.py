# MIDI Event Router

from ..core.logger import Logger

class EventRouter:
    def __init__(self, event_bus):
        self.event_bus = event_bus
        Logger.info("EventRouter initialized.")

    def route(self, midi_event):
        """Route parsed MIDI event to the correct event bus channel."""
        try:
            event_type = midi_event.get("type")

            if event_type in ("note_on", "note_off"):
                self.event_bus.publish("note_event", midi_event)

            elif event_type == "control_change":
                self.event_bus.publish("control_event", midi_event)

            else:
                Logger.warning(f"Unknown MIDI event type: {event_type}")

        except Exception as e:
            Logger.error(f"EventRouter error: {e}")

