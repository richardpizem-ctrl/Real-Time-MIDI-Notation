"""Route normalized messages on the main thread."""
class EventRouter:
    def __init__(self, event_bus, **unused):
        self.event_bus = event_bus
    def route(self, event):
        if not isinstance(event, dict):
            return
        kind = 'note_event' if event.get('type') in ('note_on','note_off') else 'control_event'
        self.event_bus.publish(kind, event)
