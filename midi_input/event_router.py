# MIDI Event Router

from ..core.logger import Logger


class EventRouter:
    def __init__(
        self,
        event_bus,
        ui_manager=None,
        notation_processor=None,
        track_system=None,
    ):
        """
        event_bus          = centrálny EventBus
        ui_manager         = UIManager (vizuálne komponenty)
        notation_processor = NotationProcessor (harmónia, rytmus, timeline)
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
        if not isinstance(midi_event, dict):
            Logger.warning(f"Invalid midi_event (not dict): {midi_event}")
            return

        try:
            event_type = midi_event.get("type")
            note = midi_event.get("note")
            velocity = midi_event.get("velocity", 0)
            channel = midi_event.get("channel", 0)

            if not isinstance(event_type, str):
                Logger.warning(f"Missing or invalid event_type: {midi_event}")
                return

            # Normalize values
            try:
                velocity = int(velocity)
            except Exception:
                velocity = 0

            try:
                channel = int(channel)
            except Exception:
                channel = 0

            if channel < 0 or channel > 15:
                channel = 0

            event = None

            # ---------------------------------------------------------
            # TRACK SYSTEM PREPOJENIE
            # ---------------------------------------------------------
            if self.track_system and event_type in ("note_on", "note_off"):
                try:
                    active_track = self.track_system.set_active_track_by_channel(channel)
                except Exception as e:
                    Logger.error(f"TrackSystem set_active_track_by_channel error: {e}")
                    active_track = None

                try:
                    event = self.track_system.build_note_event_for_active_track(
                        note=note,
                        velocity=velocity,
                        event_type=event_type,
                    )
                except Exception as e:
                    Logger.error(f"TrackSystem build_note_event_for_active_track error: {e}")
                    event = None

                if isinstance(event, dict):
                    midi_event["track_id"] = event.get("track_id")
                    midi_event["track_color"] = event.get("track_color")

                Logger.debug(
                    f"Track routing: channel={channel}, active_track={active_track}, event={event}"
                )

            # ---------------------------------------------------------
            # NOTE ON / NOTE OFF
            # ---------------------------------------------------------
            if event_type in ("note_on", "note_off"):

                # EventBus
                if self.event_bus:
                    try:
                        self.event_bus.publish("note_event", midi_event)
                    except Exception as e:
                        Logger.error(f"EventBus publish note_event error: {e}")

                # UIManager
                if self.ui and isinstance(event, dict):
                    try:
                        if event_type == "note_on" and velocity > 0:
                            self.ui.on_note_on(event)
                        else:
                            self.ui.on_note_off(event)
                    except Exception as e:
                        Logger.error(f"UIManager note handler error: {e}")

                # NotationProcessor
                if self.notation:
                    try:
                        self.notation.process_midi_event(
                            {
                                "type": event_type,
                                "note": note,
                                "velocity": velocity,
                                "time": midi_event.get("timestamp", 0.0),
                                "channel": channel,
                            }
                        )
                    except Exception as e:
                        Logger.error(f"NotationProcessor process_midi_event error: {e}")

            # ---------------------------------------------------------
            # CONTROL CHANGE
            # ---------------------------------------------------------
            elif event_type == "control_change":
                if self.event_bus:
                    try:
                        self.event_bus.publish("control_event", midi_event)
                    except Exception as e:
                        Logger.error(f"EventBus publish control_event error: {e}")

            # ---------------------------------------------------------
            # UNKNOWN EVENT TYPE
            # ---------------------------------------------------------
            else:
                Logger.warning(f"Unknown MIDI event type: {event_type}")

        except Exception as e:
            Logger.error(f"EventRouter error: {e}")

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
