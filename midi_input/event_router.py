# MIDI Event Router

from ..core.logger import Logger


class EventRouter:
    def __init__(
        self,
        event_bus,
        piano_roll_ui=None,
        staff_ui=None,
        note_visualizer=None,
        track_system=None
    ):
        """
        event_bus        = centrálny EventBus
        piano_roll_ui    = inštancia PianoRollUI
        staff_ui         = inštancia StaffUI
        note_visualizer  = inštancia NoteVisualizerUI
        track_system     = TrackSystem (16 MIDI stôp)
        """
        self.event_bus = event_bus
        self.piano_roll = piano_roll_ui
        self.staff_ui = staff_ui
        self.note_visualizer = note_visualizer
        self.track_system = track_system

        Logger.info("EventRouter initialized.")

    # ---------------------------------------------------------
    # ROUTING MIDI EVENTOV
    # ---------------------------------------------------------
    def route(self, midi_event):
        """
        midi_event je dict:
        {
            "type": "note_on" / "note_off" / "control_change",
            "note": int,
            "velocity": int,
            "channel": int,
            "timestamp": float
        }
        """
        try:
            event_type = midi_event.get("type")
            note = midi_event.get("note")
            velocity = midi_event.get("velocity", 0)
            channel = midi_event.get("channel", 0) + 1  # MIDI kanály 1–16

            # ---------------------------------------------------------
            # 🔥 PREPOJENIE TRACK SYSTEMU
            # ---------------------------------------------------------
            event = None
            if self.track_system and event_type in ("note_on", "note_off"):

                # 1) automatické prepnutie tracku podľa MIDI kanála
                self.track_system.set_active_track_by_channel(channel)

                # 2) vytvorenie note eventu
                event = self.track_system.build_note_event_for_active_track(
                    note=note,
                    velocity=velocity,
                    event_type=event_type
                )

            # ---------------------------------------------------------
            # NOTE ON / NOTE OFF
            # ---------------------------------------------------------
            if event_type in ("note_on", "note_off"):

                # Posielame do EventBus
                self.event_bus.publish("note_event", midi_event)

                # ---------------------------------------------------------
                # 🔥 Piano Roll UI
                # ---------------------------------------------------------
                if self.piano_roll:
                    if event_type == "note_on" and velocity > 0:
                        color = event["track_color"] if event else (255, 80, 80)
                        self.piano_roll.highlight_key(note, color=color)
                    else:
                        self.piano_roll.unhighlight_key(note)

                # ---------------------------------------------------------
                # 🔥 Staff UI
                # ---------------------------------------------------------
                if self.staff_ui and event:
                    if event_type == "note_on" and velocity > 0:
                        self.staff_ui.add_note(event)
                    else:
                        self.staff_ui.remove_note(event)

                # ---------------------------------------------------------
                # 🔥 Note Visualizer
                # ---------------------------------------------------------
                if self.note_visualizer and event:
                    if event_type == "note_on" and velocity > 0:
                        self.note_visualizer.on_note(event)
                    else:
                        self.note_visualizer.on_note_off(event)

            # ---------------------------------------------------------
            # CONTROL CHANGE
            # ---------------------------------------------------------
            elif event_type == "control_change":
                self.event_bus.publish("control_event", midi_event)

            # ---------------------------------------------------------
            # UNKNOWN
            # ---------------------------------------------------------
            else:
                Logger.warning(f"Unknown MIDI event type: {event_type}")

        except Exception as e:
            Logger.error(f"EventRouter error: {e}")
