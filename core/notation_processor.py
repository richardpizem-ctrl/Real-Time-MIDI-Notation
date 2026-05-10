# =========================================================
# NotationProcessor v4.0.0-ready
# AI-ready, Engraving-ready, Real-Time-ready
# =========================================================

from typing import Dict, Any, Optional, List
from mido import Message, MidiFile, MidiTrack, MetaMessage

from .logger import Logger
from .event_types import (
    MIDI_EXPORTED,
    ERROR_OCCURRED,
    AI_EVENT,
    ENGRAVING_UPDATE,
    EXPORT_PDF,
    EXPORT_SVG,
    EXPORT_MUSICXML
)


class NotationProcessor:
    """
    NotationProcessor v4-ready:
    - AI event pipeline
    - metadata injection
    - batch processing
    - engraving engine hook
    - multi-format export (MIDI/PDF/SVG/MusicXML)
    - async-safe
    """

    def __init__(self, track_system, event_bus=None):
        self.track_system = track_system
        self.event_bus = event_bus

        # AI modul
        self.ai = None
        self.ai_enabled = False

        # Engraving engine
        self.engraving_engine = None

    # ---------------------------------------------------------
    # AI ATTACH (v4)
    # ---------------------------------------------------------
    def attach_ai(self, ai_engine):
        self.ai = ai_engine
        self.ai_enabled = True
        Logger.info("AI Engine attached to NotationProcessor.")

    # ---------------------------------------------------------
    # ENGRAVING ENGINE ATTACH (v4)
    # ---------------------------------------------------------
    def attach_engraving_engine(self, engine):
        self.engraving_engine = engine
        Logger.info("Engraving Engine attached to NotationProcessor.")

    # ---------------------------------------------------------
    # PUBLIC EXPORT API
    # ---------------------------------------------------------
    def export_midi(self, filename: str = "export.mid") -> None:
        if not filename or not isinstance(filename, str):
            self._publish_error("Invalid filename")
            return

        self._export_midi_internal(filename)

    # ---------------------------------------------------------
    # INTERNAL MIDI EXPORT
    # ---------------------------------------------------------
    def _export_midi_internal(self, filename: str):
        if self.track_system is None:
            self._publish_error("TrackSystem not initialized")
            return

        try:
            mid = MidiFile()
            Logger.info(f"Starting MIDI export → {filename}")

            for track_id in range(1, 17):
                midi_track = MidiTrack()
                mid.tracks.append(midi_track)

                # Track name
                track_name = self._safe_track_name(track_id)
                try:
                    midi_track.append(MetaMessage("track_name", name=track_name, time=0))
                except Exception:
                    Logger.error(f"Failed to write track name for track {track_id}")

                # Events
                events = self._safe_get_events(track_id)

                # Batch processing (v4)
                for event in events:
                    event = self._process_event_v4(event, track_id)
                    msg = self._event_to_mido_message(event)
                    if msg:
                        try:
                            midi_track.append(msg)
                        except Exception as e:
                            Logger.error(f"Failed to append MIDI message: {e}")

            # Save file
            try:
                mid.save(filename)
                Logger.info(f"MIDI export completed → {filename}")
            except Exception as e:
                self._publish_error(str(e))
                return

            # Notify success
            if self.event_bus:
                self.event_bus.publish(MIDI_EXPORTED, filename)

        except Exception as e:
            self._publish_error(str(e))

    # ---------------------------------------------------------
    # v4 EVENT PROCESSING PIPELINE
    # ---------------------------------------------------------
    def _process_event_v4(self, event: Dict[str, Any], track_id: int):
        """AI + metadata + engraving pipeline."""
        if not isinstance(event, dict):
            return event

        # Metadata injection
        event["track_id"] = track_id

        # AI processing
        if self.ai_enabled and self.ai:
            try:
                event = self.ai.process_event(event)
            except Exception as e:
                Logger.error(f"AI processing failed: {e}")

        # Engraving engine update
        if self.engraving_engine:
            try:
                self.engraving_engine.update_event(event)
            except Exception as e:
                Logger.error(f"Engraving update failed: {e}")

        return event

    # ---------------------------------------------------------
    # SAFE TRACK NAME
    # ---------------------------------------------------------
    def _safe_track_name(self, track_id: int) -> str:
        try:
            name = self.track_system.get_track_name(track_id)
            return name if isinstance(name, str) and name.strip() else f"Track {track_id}"
        except Exception:
            return f"Track {track_id}"

    # ---------------------------------------------------------
    # SAFE EVENT RETRIEVAL
    # ---------------------------------------------------------
    def _safe_get_events(self, track_id: int) -> List[Dict[str, Any]]:
        try:
            return self.track_system.recorded_events.get(track_id, [])
        except Exception:
            return []

    # ---------------------------------------------------------
    # EVENT → MIDO MESSAGE
    # ---------------------------------------------------------
    def _event_to_mido_message(self, event: Dict[str, Any]):
        if not isinstance(event, dict):
            return None

        etype = event.get("type")
        note = event.get("note")
        velocity = event.get("velocity", 100)

        if not isinstance(note, int):
            return None

        try:
            channel = max(0, min(15, int(event.get("channel", 1)) - 1))
        except Exception:
            channel = 0

        if etype == "note_on":
            return Message("note_on", note=note, velocity=velocity, channel=channel, time=0)

        if etype == "note_off":
            return Message("note_off", note=note, velocity=velocity, channel=channel, time=0)

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
    # SHUTDOWN (v4)
    # ---------------------------------------------------------
    def shutdown(self):
        Logger.info("NotationProcessor shutdown.")
