# MIDI Event Router

from ..core.logger import Logger


class EventRouter:
    def __init__(
        self,
        event_bus,
        ui_manager=None,
        notation_processor=None,
        track_system=None
    ):
        """
        event_bus          = centrálny EventBus
        ui_manager         = UIManager (obsahuje piano, staff, vizualizér, renderer)
        notation_processor = NotationProcessor (timeline, harmónia, rytmus)
        track_system       = TrackSystem (16 MIDI stôp)
        """
        self.event_bus = event_bus
        self.ui = ui_manager
        self.notation = notation_processor
        self.track_system = track_system

        Logger.info("EventRouter initialized.")


    # ---------------------------------------------------------
    # ROUTING MIDI EVENTOV
    # ---------------------------------------------------------
    def route(self, midi_event: dict):
        """
        midi_event je dict:
        {
            "type": "note_on" / "note_off" / "control_change",
            "note": int,
            "velocity": int,
            "channel": int,   # 0–15
            "timestamp": float
        }
        """
        try:
            event_type = midi_event.get("type")
            note = midi_event.get("note")
            velocity = midi_event.get("velocity", 0)
            channel = midi_event.get("channel", 0)

            # ---------------------------------------------------------
            # 🔥 PREPOJENIE TRACK SYSTEMU
            # ---------------------------------------------------------
            event = None
            if self.track_system and event_type in ("note_on", "note_off"):

                # 1) automatické prepnutie tracku podľa MIDI kanála
                active_track = self.track_system.set_active_track_by_channel(channel)

                # 2) vytvorenie note eventu pre aktívny track
                event = self.track_system.build_note_event_for_active_track(
                    note=note,
                    velocity=velocity,
                    event_type=event_type
                )

                if event:
                    midi_event["track_id"] = event.get("track_id")
                    midi_event["track_color"] = event.get("track_color")

                Logger.debug(
                    f"Track routing: channel={channel}, active_track={active_track}, event={event}"
                )

            # ---------------------------------------------------------
            # NOTE ON / NOTE OFF
            # ---------------------------------------------------------
            if event_type in ("note_on", "note_off"):

                # Posielame do EventBus (aj s track_id)
                if self.event_bus:
                    self.event_bus.publish("note_event", midi_event)

                # ---------------------------------------------------------
                # 🔥 UIManager (hlavné UI reakcie)
                # ---------------------------------------------------------
                if self.ui and event:
                    if event_type == "note_on" and velocity > 0:
                        self.ui.on_note_on(event)
                    else:
                        self.ui.on_note_off(event)

                # ---------------------------------------------------------
                # 🔥 NotationProcessor (timeline, harmónia, rytmus)
                # ---------------------------------------------------------
                if self.notation:
                    self.notation.process_midi_event({
                        "type": event_type,
                        "note": note,
                        "velocity": velocity,
                        "time": midi_event.get("timestamp", 0.0),
                        "channel": channel,
                    })

            # ---------------------------------------------------------
            # CONTROL CHANGE
            # ---------------------------------------------------------
            elif event_type == "control_change":
                if self.event_bus:
                    self.event_bus.publish("control_event", midi_event)

            # ---------------------------------------------------------
            # UNKNOWN
            # ---------------------------------------------------------
            else:
                Logger.warning(f"Unknown MIDI event type: {event_type}")

        except Exception as e:
            Logger.error(f"EventRouter error: {e}")
