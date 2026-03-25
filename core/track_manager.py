# Správa 16 MIDI traktov (stôp)

from dataclasses import dataclass
from typing import Optional, Dict, Any, List, Tuple
from core.config_manager import ConfigManager

# 🔵 Import event typov
from .event_types import (
    NOTE_RECORDED,
    TRACK_SELECTED,
    TRACK_NAME_CHANGED
)

# ---------------------------------------------------------
# FARBY PRE 16 TRACKOV (MIDI KANÁLY 1–16)
# ---------------------------------------------------------
TRACK_COLORS: Dict[int, Tuple[int, int, int]] = {
    1:  (255, 99, 132),
    2:  (54, 162, 235),
    3:  (255, 206, 86),
    4:  (75, 192, 192),
    5:  (153, 102, 255),
    6:  (255, 159, 64),
    7:  (255, 255, 255),
    8:  (200, 200, 200),
    9:  (255, 0, 128),
    10: (0, 255, 128),
    11: (128, 0, 255),
    12: (0, 200, 255),
    13: (255, 200, 0),
    14: (0, 255, 200),
    15: (200, 0, 255),
    16: (128, 128, 128),
}


@dataclass
class Track:
    id: int
    name: str
    channel: int
    enabled: bool = True
    color: Tuple[int, int, int] = (255, 255, 255)


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
        self.recorded_events: Dict[int, List[Dict[str, Any]]] = {
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
            color = TRACK_COLORS.get(i, (255, 255, 255))
            self.tracks[i] = Track(
                id=i,
                name=f"Track {i}",
                channel=i,
                enabled=True,
                color=color
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
    # LIST / GET – PODPORA PRE UI
    # ---------------------------------------------------------
    def list_tracks(self) -> List[Track]:
        return list(self.tracks.values())

    def get_track_name(self, track_id: int) -> Optional[str]:
        track = self.tracks.get(track_id)
        return track.name if track else None

    def get_active_track(self) -> Optional[Track]:
        if self.active_track_id is None:
            return None
        return self.tracks.get(self.active_track_id)

    def get_track_color(self, track_id: int) -> Optional[Tuple[int, int, int]]:
        track = self.tracks.get(track_id)
        return track.color if track else None

    def get_ui_track_list(self) -> List[Dict[str, Any]]:
        """
        Stručná štruktúra pre UI:
        - id
        - name
        - channel
        - enabled
        - color
        - is_active
        """
        return [
            {
                "id": t.id,
                "name": t.name,
                "channel": t.channel,
                "enabled": t.enabled,
                "color": t.color,
                "is_active": (t.id == self.active_track_id),
            }
            for t in self.tracks.values()
        ]

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
        track = self.tracks[track_id]
        print(f"[TrackSystem] Aktívny trakt: {track_id} ({track.name})")

        # 🔵 Publikujeme event o zmene aktívneho traktu
        if self.event_bus:
            self.event_bus.publish(TRACK_SELECTED, {
                "track_id": track_id,
                "name": track.name,
                "channel": track.channel,
                "color": track.color,
            })

        return True

    def set_active_track_by_channel(self, channel: int) -> bool:
        """
        Automatické prepnutie aktívneho tracku podľa MIDI kanála.
        Použiteľné pri realtime MIDI vstupoch.
        """
        for track in self.tracks.values():
            if track.channel == channel and track.enabled:
                return self.set_active_track(track.id)

        print(f"[TrackSystem] Žiadny aktívny track pre channel {channel}.")
        return False

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
            "track_color": track.color,
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
