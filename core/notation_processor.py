# NotationProcessor – správa notových udalostí a export MIDI podľa trakov

from typing import Dict, Any
from mido import Message, MidiFile, MidiTrack, MetaMessage


class NotationProcessor:
    """
    Procesor notácie, ktorý:
    - pracuje s TrackSystem
    - exportuje MIDI podľa trakov (každý trakt = jedna MIDI stopa)
    """

    def __init__(self, track_system):
        """
        track_system: inštancia TrackSystem z core.track_manager
        """
        self.track_system = track_system

    def export_to_midi(self, filename: str = "export.mid") -> None:
        """
        Exportuje všetky zaznamenané udalosti z TrackSystem.recorded_events
        do jedného MIDI súboru, kde:
        - každý trakt má vlastnú MIDI stopu
        - názov traktu sa použije ako názov stopy
        """
        mid = MidiFile()

        # pre každý trakt vytvoríme jednu MIDI stopu
        for track_id in range(1, 17):
            midi_track = MidiTrack()
            mid.tracks.append(midi_track)

            # názov traktu
            track_name = self.track_system.get_track_name(track_id) or f"Track {track_id}"
            midi_track.append(MetaMessage("track_name", name=track_name, time=0))

            # eventy z TrackSystem
            events = self.track_system.recorded_events.get(track_id, [])

            for event in events:
                msg = self._event_to_mido_message(event)
                if msg is not None:
                    midi_track.append(msg)

        mid.save(filename)
        print(f"[NotationProcessor] MIDI exportované do súboru: {filename}")

    def _event_to_mido_message(self, event: Dict[str, Any]) -> Any:
        """
        Konvertuje dict event (z TrackSystem.build_note_event_for_track)
        na Mido Message.
        """
        etype = event.get("type")
        note = event.get("note")
        velocity = event.get("velocity", 100)
        channel = event.get("channel", 1) - 1  # Mido používa kanály 0–15

        if etype == "note_on":
            return Message(
                "note_on",
                note=note,
                velocity=velocity,
                channel=channel,
                time=0,
            )
        elif etype == "note_off":
            return Message(
                "note_off",
                note=note,
                velocity=velocity,
                channel=channel,
                time=0,
            )

        # neznámy typ eventu – ignorujeme
        return None
