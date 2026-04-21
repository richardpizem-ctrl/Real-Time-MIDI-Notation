# NotationProcessor – správa notových udalostí a export MIDI podľa trakov

from typing import Dict, Any, Optional
from mido import Message, MidiFile, MidiTrack, MetaMessage

from .logger import Logger
from .event_types import MIDI_EXPORTED, ERROR_OCCURRED


class NotationProcessor:
    """
    Procesor notácie (Fáza 4):
    - pracuje s TrackSystem
    - exportuje MIDI podľa trakov (každý track = jedna MIDI stopa)
    - odolný voči chybným eventom
    - bezpečný export
    """

    def __init__(self, track_system, event_bus=None):
        self.track_system = track_system
        self.event_bus = event_bus

        # AI modul (voliteľný)
        self.ai = None
        self.ai_enabled = False   # NOVÉ – AI sa dá zapnúť/vypnúť

    # ---------------------------------------------------------
    # AI ATTACH (NOVÉ – PRÍPRAVA NA v3.0.0)
    # ---------------------------------------------------------
    def attach_ai(self, ai_engine):
        """Pripojí AI modul k NotationProcessoru."""
        self.ai = ai_engine
        self.ai_enabled = True
        Logger.info("AI Engine attached to NotationProcessor.")

    # ---------------------------------------------------------
    # PUBLIC EXPORT API
    # ---------------------------------------------------------
    def export_midi(self, filename: str = "export.mid") -> None:
        """Externé API – volané AppControllerom."""
        if not filename or not isinstance(filename, str):
            Logger.error("NotationProcessor: invalid filename for export.")
            self._publish_error("Invalid filename")
            return

        self.export_to_midi(filename)

    # ---------------------------------------------------------
    # EXPORT MIDI
    # ---------------------------------------------------------
    def export_to_midi(self, filename: str = "export.mid") -> None:
        if self.track_system is None:
            Logger.error("NotationProcessor: track_system is None – export aborted.")
            self._publish_error("TrackSystem not initialized")
            return

        try:
            mid = MidiFile()
            Logger.info(f"Starting MIDI export → {filename}")

            # Pre každý track vytvoríme jednu MIDI stopu
            for track_id in range(1, 17):
                midi_track = MidiTrack()
                mid.tracks.append(midi_track)

                # Názov tracku
                try:
                    track_name = self.track_system.get_track_name(track_id)
                    if not isinstance(track_name, str) or not track_name.strip():
                        track_name = f"Track {track_id}"
                except Exception:
                    track_name = f"Track {track_id}"

                try:
                    midi_track.append(MetaMessage("track_name", name=track_name, time=0))
                except Exception:
                    Logger.error(f"Failed to write track name for track {track_id}")

                # Eventy z TrackSystem
                try:
                    events = self.track_system.recorded_events.get(track_id, [])
                except Exception:
                    events = []

                for event in events:

                    # ---------------------------------------------------------
                    # AI HOOK (NOVÉ – PRÍPRAVA NA v3.0.0)
                    # ---------------------------------------------------------
                    if self.ai_enabled and self.ai:
                        try:
                            event = self.ai.process_event(event)
                        except Exception as e:
                            Logger.error(f"AI processing failed: {e}")

                    msg = self._event_to_mido_message(event)
                    if msg is not None:
                        try:
                            midi_track.append(msg)
                        except Exception as e:
                            Logger.error(f"Failed to append MIDI message: {e}")

            # Uloženie súboru
            try:
                mid.save(filename)
                Logger.info(f"MIDI export completed → {filename}")
            except Exception as e:
                Logger.error(f"Failed to save MIDI file: {e}")
                self._publish_error(str(e))
                return

            # Publikujeme úspech
            if self.event_bus:
                try:
                    self.event_bus.publish(MIDI_EXPORTED, filename)
                except Exception:
                    pass

        except Exception as e:
            Logger.error(f"NotationProcessor: MIDI export failed → {e}")
            self._publish_error(str(e))

    # ---------------------------------------------------------
    # KONVERZIA EVENTU NA MIDO MESSAGE
    # ---------------------------------------------------------
    def _event_to_mido_message(self, event: Dict[str, Any]) -> Optional[Message]:
        if not isinstance(event, dict):
            Logger.warning("NotationProcessor: invalid event (not a dict)")
            return None

        etype = event.get("type")
        note = event.get("note")
        velocity = event.get("velocity", 100)

        if not isinstance(note, int):
            Logger.debug("NotationProcessor: ignored event (invalid note)")
            return None

        try:
            channel = max(0, min(15, int(event.get("channel", 1)) - 1))
        except Exception:
            channel = 0

        if etype == "note_on":
            try:
                return Message("note_on", note=note, velocity=velocity, channel=channel, time=0)
            except Exception:
                return None

        if etype == "note_off":
            try:
                return Message("note_off", note=note, velocity=velocity, channel=channel, time=0)
            except Exception:
                return None

        Logger.debug(f"NotationProcessor: ignored event type '{etype}'")
        return None

    # ---------------------------------------------------------
    # ERROR PUBLISHING
    # ---------------------------------------------------------
    def _publish_error(self, message: str):
        if self.event_bus:
            try:
                self.event_bus.publish(ERROR_OCCURRED, message)
            except Exception:
                pass

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
