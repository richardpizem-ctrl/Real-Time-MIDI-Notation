# Správa 16 MIDI traktov (stôp)

from dataclasses import dataclass
from typing import Optional, Dict, Any
from core.config_manager import ConfigManager

# 🔵 Import event typov
from .event_types import (
    NOTE_RECORDED,
    TRACK_SELECTED,
    TRACK_NAME_CHANGED
)


@dataclass
class Track:
    id: int
    name: str
    channel: int
    enabled: bool = True


class TrackSystem:
    """
    Systém 16-tich traktov s podporou názvov.
    Názvy sa ukladajú do config.json.
    """

    def __init__(self, event_bus=None):
        self.event_bus = event_bus
        self.config = ConfigManager()
        self.tracks: Dict[int, Track] = {}
        self.active_track_id: Optional[int] = None

        # 🔵 Úložisko eventov pre export MIDI
        self.recorded_events: Dict[int, list[Dict[str, Any]]] = {
            i: [] for i in range(1, 17)
        }

        self._init_tracks()
        self._load_track_names()

    # ---------------------------------------------------------
    # INIT TRAKTY
    # ---------------------------------------------------------
    def _init_tracks(self):
        """Inicializuje 16 traktov s kanálmi 1–16."""
        for i in range(1, 17):
            self.tracks[i] = Track(
                id=i,
                name=f"Track {i}",
                channel=i,
                enabled=True
            )
        self.active_track_id = 1

    # ---------------------------------------------------------
    # LOAD / SAVE NAMES
    # ---------------------------------------------------------
    def _load_track_names(self):
        """Načíta názvy trakov z config.json, ak existujú."""
        saved_names = self.config.get("track_names", {})

        for track_id, name in saved_names.items():
            track_id = int(track_id)
            if track_id in self.tracks:
                self.tracks[track_id].name = name

    def _save_track_names(self):
        """Uloží názvy trakov do config.json."""
        names = {str(t.id): t.name for t in self.tracks.values()}
        self.config.set("track_names", names)

    # ---------------------------------------------------------
    # LIST / GET
    # ---------------------------------------------------------
    def list_tracks(self):
        return list(self.tracks.values())

    def get_track_name(self, track_id: int) -> Optional[str]:
        track = self.tracks.get(track_id)
        return track.name if track else None

    def get_active_track(self) -> Optional[Track]:
        if self.active_track_id is None:
            return None
        return self.tracks.get(self.active_track_id)

    # ---------------------------------------------------------
    # RENAME TRACK
    # ---------------------------------------------------------
    def set_track_name(self, track_id: int, name: str):
        """Premenuje trakt a uloží do config.json."""
        track = self.tracks.get(track_id)
        if not track:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return False

        track.name = name
        self._save_track_names()
        print(f"[TrackSystem] Track {track_id} → nový názov: {name}")

        # 🔵 Publikujeme event o zmene názvu
        if self.event_bus:
            self.event_bus.publish(TRACK_NAME_CHANGED, {
                "track_id": track_id,
                "name": name
            })

        return True

    def rename_active_track(self, name: str):
        """Premenuje práve aktívny trakt."""
        if self.active_track_id is None:
            print("[TrackSystem] Nie je aktívny trakt.")
            return False
        return self.set_track_name(self.active_track_id, name)

    # ---------------------------------------------------------
    # ENABLE / SELECT TRACK
    # ---------------------------------------------------------
    def enable_track(self, track_id: int, enabled: bool = True):
        track = self.tracks.get(track_id)
        if not track:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return False
        track.enabled = enabled
        return True

    def set_active_track(self, track_id: int):
        if track_id not in self.tracks:
            print(f"[TrackSystem] Neplatný track_id: {track_id}")
            return False
        if not self.tracks[track_id].enabled:
            print(f"[TrackSystem] Track {track_id} je vypnutý.")
            return False

        self.active_track_id = track_id
        print(f"[TrackSystem] Aktívny trakt: {track_id} ({self.tracks[track_id].name})")

        # 🔵 Publikujeme event o zmene aktívneho traktu
        if self.event_bus:
            self.event_bus.publish(TRACK_SELECTED, track_id)

        return True

    # ---------------------------------------------------------
    # BUILD NOTE EVENT
    # ---------------------------------------------------------
    def build_note_event_for_track(
        self,
        track_id: int,
        note: int,
        velocity: int = 100,
        event_type: str = "note_on",
        time: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:

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

        # 🔵 Uloženie eventu pre export MIDI
        self.recorded_events[track_id].append(event)

        # 🔵 Publikujeme NOTE_RECORDED
        if self.event_bus:
            self.event_bus.publish(NOTE_RECORDED, event)

        return event

    def build_note_event_for_active_track(
        self,
        note: int,
        velocity: int = 100,
        event_type: str = "note_on",
        time: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:

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
