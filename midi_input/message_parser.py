# =========================================================
# EventRouter v4.3.0
# Stabilný router MIDI udalostí pre Real-Time MIDI Engine
# =========================================================

from ..core.logger import Logger


class EventRouter:
    """
    EventRouter (v4.3.0):
    - prijíma MIDI eventy z MIDIListener / StreamHandler
    - smeruje ich do TrackSystem, UIManager, NotationProcessor a EventBus
    - odolný voči chybným MIDI eventom
    - real-time safe (žiadne výnimky v slučke)
    - kompatibilný s architektúrou verzie 4.3.0
    """

    __slots__ = (
        "event_bus",
        "ui",
        "notation",
        "track_system",
    )

    def __init__(
        self,
        event_bus,
        ui_manager=None,
        notation_processor=None,
        track_system=None,
    ):
        self.event_bus = event_bus
        self.ui = ui_manager
        self.notation = notation_processor
        self.track_system = track_system

        Logger.info("EventRouter initialized (v4.3.0).")

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
            "channel": int,
            "time": float
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

            # Normalize
            try:
                velocity = int(velocity)
            except Exception:
                velocity = 0

            try:
                channel = int(channel)
            except Exception:
                channel = 0

            if not 0 <= channel <= 15:
                channel = 0

            event = None

            # ---------------------------------------------------------
            # TRACK SYSTEM
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

            # ---------------------------------------------------------
            # NOTE EVENTS
            # ---------------------------------------------------------
            if event_type in ("note_on", "note_off"):

                # EventBus
                bus = self.event_bus
                if bus:
                    try:
                        bus.publish("note_event", midi_event)
                    except Exception as e:
                        Logger.error(f"EventBus publish note_event error: {e}")

                # UIManager
                ui = self.ui
                if ui and isinstance(event, dict):
                    try:
                        if event_type == "note_on" and velocity > 0:
                            ui.on_note_on(event)
                        else:
                            ui.on_note_off(event)
                    except Exception as e:
                        Logger.error(f"UIManager note handler error: {e}")

                # NotationProcessor
                notation = self.notation
                if notation:
                    try:
                        notation.process_midi_event(
                            {
                                "type": event_type,
                                "note": note,
                                "velocity": velocity,
                                "time": midi_event.get("time", 0.0),
                                "channel": channel,
                            }
                        )
                    except Exception as e:
                        Logger.error(f"NotationProcessor process_midi_event error: {e}")

            # ---------------------------------------------------------
            # CONTROL CHANGE
            # ---------------------------------------------------------
            elif event_type == "control_change":
                bus = self.event_bus
                if bus:
                    try:
                        bus.publish("control_event", midi_event)
                    except Exception as e:
                        Logger.error(f"EventBus publish control_event error: {e}")

            # ---------------------------------------------------------
            # UNKNOWN
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
