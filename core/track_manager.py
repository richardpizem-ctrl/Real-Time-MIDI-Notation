# Správa 16 MIDI traktov (stôp)

from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class Track:
    """
    Jeden MIDI trakt (stopa).
    - id: 1–16
    - name: voliteľný názov
    - channel: MIDI kanál 1–16
    - enabled: či je trakt aktívny
    """
    id: int
    name: str
    channel: int
    enabled: bool = True


class TrackSystem:
    """
    Systém 16-tich traktov.
    Umožňuje:
    - vybrať aktívny trakt
    - posielať noty na konkrétny trakt
    - získať info o trakte
    """

    def __init__(self):
        self.tracks: Dict[int, Track] = {}
        self.active_track_id: Optional[int] = None
        self._init_tracks()

    def _init_tracks(self):
        """Inicializuje 16 traktov s kanálmi 1–16."""
        for i in range(1, 17):
            self.tracks[i] = Track(
                id=i,
                name=f"Track {i}",
                channel=i,  # MIDI kanál 1–16
                enabled=True
            )
        self.active_track_id = 1

    def list_tracks(self):
        """Vráti zoznam všetkých traktov."""
        return list(self.tracks.values())

    def set_track_name(self, track_id: int, name: str):
        """Premenuje trakt."""
        track = self.tracks.get(track_id)
        if not track:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return False
        track.name = name
        return True

    def enable_track(self, track_id: int, enabled: bool = True):
        """Zapne alebo vypne trakt."""
        track = self.tracks.get(track_id)
        if not track:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return False
        track.enabled = enabled
        return True

    def set_active_track(self, track_id: int):
        """Nastaví aktívny trakt (1–16)."""
        if track_id not in self.tracks:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return False
        if not self.tracks[track_id].enabled:
            print(f"[TrackSystem] Track {track_id} je vypnutý.")
            return False
        self.active_track_id = track_id
        print(f"[TrackSystem] Aktívny trakt: {track_id} ({self.tracks[track_id].name})")
        return True

    def get_active_track(self) -> Optional[Track]:
        """Vráti aktuálne aktívny trakt."""
        if self.active_track_id is None:
            return None
        return self.tracks.get(self.active_track_id)

    def build_note_event_for_track(
        self,
        track_id: int,
        note: int,
        velocity: int = 100,
        event_type: str = "note_on",
        time: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Vytvorí MIDI event pre konkrétny trakt.
        Výstup je dict, ktorý môžeš poslať ďalej do NotationProcessor / MIDI sendera.
        """
        track = self.tracks.get(track_id)
        if not track:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return None
        if not track.enabled:
            print(f"[TrackSystem] Track {track_id} je vypnutý.")
            return None

        event = {
            "type": event_type,
            "note": note,
            "velocity": velocity,
            "channel": track.channel,
            "track_id": track.id,
            "track_name": track.name,
            "time": time,
        }
        return event

    def build_note_event_for_active_track(
        self,
        note: int,
        velocity: int = 100,
        event_type: str = "note_on",
        time: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Vytvorí MIDI event pre aktuálne aktívny trakt.
        """
        if self.active_track_id is None:
            print("[TrackSystem] Nie je nastavený aktívny trakt.")
            return None
        return self.build_note_event_for_track(
            self.active_track_id,
            note=note,
            velocity=velocity,
            event_type=event_type,
            time=time,
        )
