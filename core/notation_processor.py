# NotationProcessor – správa notových udalostí a export MIDI podľa trakov

from typing import Dict, Any, Optional
from mido import Message, MidiFile, MidiTrack, MetaMessage

from .logger import Logger
from .event_types import MIDI_EXPORTED, ERROR_OCCURRED


class NotationProcessor:
    """
    Procesor notácie, ktorý:
    - pracuje s TrackSystem
    - exportuje MIDI podľa trakov (každý track = jedna MIDI stopa)
    """

    def __init__(self, track_system, event_bus=None):
        """
        track_system: inštancia TrackSystem
        event_bus: EventBus pre publikovanie udalostí
        """
        self.track_system = track_system
        self.event_bus = event_bus

    # ---------------------------------------------------------
    # PUBLIC EXPORT API (volané z AppController)
    # ---------------------------------------------------------
    def export_midi(self, filename: str = "export.mid") -> None:
        """Externé API – volané AppControllerom."""
        self.export_to_midi(filename)

    # ---------------------------------------------------------
    # EXPORT MIDI
    # ---------------------------------------------------------
    def export_to_midi(self, filename: str = "export.mid") -> None:
        """
        Exportuje všetky zaznamenané udalosti z TrackSystem.recorded_events
        do jedného MIDI súboru:
        - každý track má vlastnú MIDI stopu
        - názov tracku sa použije ako názov stopy
        """
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
                track_name = self.track_system.get_track_name(track_id) or f"Track {track_id}"
                midi_track.append(MetaMessage("track_name", name=track_name, time=0))

                # Eventy z TrackSystem
                events = self.track_system.recorded_events.get(track_id, [])
                if not events:
                    continue

                for event in events:
                    msg = self._event_to_mido_message(event)
                    if msg is not None:
                        midi_track.append(msg)

            # Uloženie súboru
            mid.save(filename)
            Logger.info(f"MIDI export completed → {filename}")

            # Publikujeme úspech
            if self.event_bus:
                self.event_bus.publish(MIDI_EXPORTED, filename)

        except Exception as e:
            Logger.error(f"NotationProcessor: MIDI export failed → {e}")
            self._publish_error(str(e))

    # ---------------------------------------------------------
    # KONVERZIA EVENTU NA MIDO MESSAGE
    # ---------------------------------------------------------
    def _event_to_mido_message(self, event: Dict[str, Any]) -> Optional[Message]:
        """
        Konvertuje dict event (z TrackSystem.build_note_event_for_track)
        na Mido Message.
        """
        if not isinstance(event, dict):
            Logger.warning("NotationProcessor: invalid event (not a dict)")
            return None

        etype = event.get("type")
        note = event.get("note")
        velocity = event.get("velocity", 100)
        channel = max(0, min(15, event.get("channel", 1) - 1))  # Mido používa kanály 0–15

        if etype == "note_on":
            return Message(
                "note_on",
                note=note,
                velocity=velocity,
                channel=channel,
                time=0,
            )

        if etype == "note_off":
            return Message(
                "note_off",
                note=note,
                velocity=velocity,
                channel=channel,
                time=0,
            )

        # Neznámy typ eventu – ignorujeme
        Logger.debug(f"NotationProcessor: ignored event type '{etype}'")
        return None

    # ---------------------------------------------------------
    # ERROR PUBLISHING
    # ---------------------------------------------------------
    def _publish_error(self, message: str):
        """Publikuje chybu do EventBusu."""
        if self.event_bus:
            try:
                self.event_bus.publish(ERROR_OCCURRED, message)
            except Exception:
                pass
