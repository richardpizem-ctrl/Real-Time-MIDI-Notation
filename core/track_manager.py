"""
TrackManager – vizuálna a logická vrstva pre renderer a UI.
Prepája sa priamo s TrackSystem (16 MIDI kanálov).
"""

from typing import Dict, Tuple, Optional, List
from core.track_manager import TrackSystem
from core.logger import Logger


class TrackManager:
    def __init__(self, track_system: TrackSystem):
        self.track_system = track_system

        # Visibility of tracks (UI + Renderer)
        self.track_visibility: Dict[int, bool] = {i: True for i in range(1, 17)}

        # Active track (UI selection)
        self.active_track: int = 1

        # Mute / Solo states
        self.mute: Dict[int, bool] = {i: False for i in range(1, 17)}
        self.solo: Dict[int, bool] = {i: False for i in range(1, 17)}

        # Volume / Pan
        self.volume: Dict[int, float] = {i: 1.0 for i in range(1, 17)}
        self.pan: Dict[int, float] = {i: 0.0 for i in range(1, 17)}

        # Record arm
        self.record_arm: Dict[int, bool] = {i: False for i in range(1, 17)}

        # Real-time activity (renderer → TrackManager → UI)
        self.activity: Dict[int, float] = {i: 0.0 for i in range(1, 17)}

    # ---------------------------------------------------------
    # ACTIVE TRACK
    # ---------------------------------------------------------
    def set_active_track(self, track_id: int):
        if not isinstance(track_id, int):
            Logger.warning(f"TrackManager.set_active_track: invalid track_id {track_id}")
            return

        if 1 <= track_id <= 16:
            self.active_track = track_id
        else:
            Logger.warning(f"TrackManager.set_active_track: out of range {track_id}")

    def get_active_track(self) -> int:
        return self.active_track

    def handle_track_selected(self, track_id: int):
        self.set_active_track(track_id)

    # ---------------------------------------------------------
    # VISIBILITY
    # ---------------------------------------------------------
    def set_visible(self, track_id: int, visible: bool):
        if not isinstance(track_id, int):
            Logger.warning(f"TrackManager.set_visible: invalid track_id {track_id}")
            return

        if track_id in self.track_visibility:
            self.track_visibility[track_id] = bool(visible)

    def toggle(self, track_id: int):
        if not isinstance(track_id, int):
            Logger.warning(f"TrackManager.toggle: invalid track_id {track_id}")
            return

        if track_id in self.track_visibility:
            self.track_visibility[track_id] = not self.track_visibility[track_id]

    def is_visible(self, track_id: int) -> bool:
        if not isinstance(track_id, int):
            return True
        return self.track_visibility.get(track_id, True)

    def get_visible_tracks(self) -> List[int]:
        try:
            return [tid for tid, v in self.track_visibility.items() if v]
        except Exception as e:
            Logger.error(f"TrackManager.get_visible_tracks error: {e}")
            return []

    # ---------------------------------------------------------
    # COLORS
    # ---------------------------------------------------------
    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        """
        Vráti RGB farbu stopy.
        Ak TrackSystem vráti nevalidné dáta, použije sa fallback.
        """
        try:
            color = self.track_system.get_track_color(track_id)
            if (
                isinstance(color, (tuple, list))
                and len(color) == 3
                and all(isinstance(c, int) for c in color)
            ):
                return tuple(color)
        except Exception as e:
            Logger.error(f"TrackManager.get_color error: {e}")

        return (255, 255, 255)

    # ---------------------------------------------------------
    # NAMES
    # ---------------------------------------------------------
    def get_name(self, track_id: int) -> str:
        try:
            name = self.track_system.get_track_name(track_id)
            if isinstance(name, str) and name.strip():
                return name
        except Exception as e:
            Logger.error(f"TrackManager.get_name error: {e}")

        return f"Track {track_id}"

    # ---------------------------------------------------------
    # MUTE / SOLO
    # ---------------------------------------------------------
    def set_mute(self, track_id: int, state: bool):
        if track_id in self.mute:
            self.mute[track_id] = bool(state)

    def is_muted(self, track_id: int) -> bool:
        return self.mute.get(track_id, False)

    def set_solo(self, track_id: int, state: bool):
        if track_id in self.solo:
            self.solo[track_id] = bool(state)

    def is_solo(self, track_id: int) -> bool:
        return self.solo.get(track_id, False)

    def solo_mode_active(self) -> bool:
        return any(self.solo.values())

    # ---------------------------------------------------------
    # EFFECTIVE ACTIVE STATE (DAW-úroveň logiky)
    # ---------------------------------------------------------
    def is_effectively_active(self, track_id: int) -> bool:
        """
        DAW logika:
        - ak je solo mód aktívny → hrajú iba solo stopy
        - mute vždy vypína stopu
        """
        if track_id not in self.mute:
            return True

        if self.is_muted(track_id):
            return False

        if self.solo_mode_active():
            return self.is_solo(track_id)

        return True

    # ---------------------------------------------------------
    # RECORD ARM
    # ---------------------------------------------------------
    def toggle_record_arm(self, track_id: int):
        if track_id in self.record_arm:
            self.record_arm[track_id] = not self.record_arm[track_id]

    def set_record_arm(self, track_id: int, state: bool):
        if track_id in self.record_arm:
            self.record_arm[track_id] = bool(state)

    def is_record_armed(self, track_id: int) -> bool:
        return self.record_arm.get(track_id, False)

    # ---------------------------------------------------------
    # VOLUME / PAN
    # ---------------------------------------------------------
    def set_volume(self, track_id: int, volume: float):
        if track_id in self.volume:
            volume = max(0.0, min(1.0, float(volume)))
            self.volume[track_id] = volume

    def get_volume(self, track_id: int) -> float:
        return self.volume.get(track_id, 1.0)

    def set_pan(self, track_id: int, pan: float):
        if track_id in self.pan:
            pan = max(-1.0, min(1.0, float(pan)))
            self.pan[track_id] = pan

    def get_pan(self, track_id: int) -> float:
        return self.pan.get(track_id, 0.0)

    # ---------------------------------------------------------
    # REAL-TIME ACTIVITY (RENDERER → TRACKMANAGER → UI)
    # ---------------------------------------------------------
    def update_activity(self, track_id: int, level: float):
        """
        Nastaví aktuálnu aktivitu stopy v rozsahu 0.0–1.0.
        Renderer to volá podľa realtime energie/velocity.
        """
        if track_id not in self.activity:
            return

        try:
            level = float(level)
        except Exception:
            return

        level = max(0.0, min(1.0, level))
        self.activity[track_id] = level

    def get_activity(self, track_id: int) -> float:
        """
        Vráti aktuálnu aktivitu stopy (0.0–1.0).
        UI to používa pre peak meter.
        """
        return self.activity.get(track_id, 0.0)

    # ---------------------------------------------------------
    # APPLY TO MIDI ENGINE
    # ---------------------------------------------------------
    def apply_midi_transform(self, track_id: int, note: int, velocity: int) -> Optional[Tuple[int, int]]:
        """
        Aplikuje DAW logiku na MIDI event:
        - mute / solo
        - volume scaling
        """
        if not self.is_effectively_active(track_id):
            return None

        vol = self.get_volume(track_id)
        velocity = int(velocity * vol)

        if velocity < 1:
            return None

        return note, velocity
