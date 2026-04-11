"""
TrackManager – vizuálna a logická vrstva pre renderer a UI.
Prepája sa s TrackSystem (16 MIDI kanálov) cez dependency injection.
"""

from typing import Dict, Tuple, Optional, List
from core.logger import Logger


class TrackManager:
    def __init__(self, track_system):
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
    # INTERNAL: CLAMP
    # ---------------------------------------------------------
    def _clamp(self, track_id: int) -> Optional[int]:
        try:
            tid = int(track_id)
        except Exception:
            return None
        if 1 <= tid <= 16:
            return tid
        return None

    # ---------------------------------------------------------
    # ACTIVE TRACK
    # ---------------------------------------------------------
    def set_active_track(self, track_id: int):
        tid = self._clamp(track_id)
        if tid is None:
            Logger.warning(f"TrackManager.set_active_track: invalid track_id {track_id}")
            return
        self.active_track = tid

    def get_active_track(self) -> int:
        return self.active_track

    def handle_track_selected(self, track_id: int):
        self.set_active_track(track_id)

    # ---------------------------------------------------------
    # VISIBILITY
    # ---------------------------------------------------------
    def set_visible(self, track_id: int, visible: bool):
        tid = self._clamp(track_id)
        if tid:
            self.track_visibility[tid] = bool(visible)

    def toggle(self, track_id: int):
        tid = self._clamp(track_id)
        if tid:
            self.track_visibility[tid] = not self.track_visibility[tid]

    def is_visible(self, track_id: int) -> bool:
        tid = self._clamp(track_id)
        if tid is None:
            return True
        return self.track_visibility.get(tid, True)

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
        tid = self._clamp(track_id)
        if tid is None or self.track_system is None:
            return (255, 255, 255)

        try:
            color = self.track_system.get_track_color(tid)
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
        tid = self._clamp(track_id)
        if tid is None or self.track_system is None:
            return f"Track {track_id}"

        try:
            name = self.track_system.get_track_name(tid)
            if isinstance(name, str) and name.strip():
                return name
        except Exception as e:
            Logger.error(f"TrackManager.get_name error: {e}")

        return f"Track {tid}"

    # ---------------------------------------------------------
    # MUTE / SOLO
    # ---------------------------------------------------------
    def set_mute(self, track_id: int, state: bool):
        tid = self._clamp(track_id)
        if tid:
            self.mute[tid] = bool(state)

    def is_muted(self, track_id: int) -> bool:
        tid = self._clamp(track_id)
        return self.mute.get(tid, False)

    def set_solo(self, track_id: int, state: bool):
        tid = self._clamp(track_id)
        if tid:
            self.solo[tid] = bool(state)

    def is_solo(self, track_id: int) -> bool:
        tid = self._clamp(track_id)
        return self.solo.get(tid, False)

    def solo_mode_active(self) -> bool:
        return any(self.solo.values())

    # Exclusive mute (CTRL)
    def mute_exclusive(self, track_id: int):
        tid = self._clamp(track_id)
        if tid is None:
            return
        for t in self.mute:
            self.mute[t] = (t == tid)

    # Exclusive solo (SHIFT)
    def solo_exclusive(self, track_id: int):
        tid = self._clamp(track_id)
        if tid is None:
            return
        for t in self.solo:
            self.solo[t] = (t == tid)

    # ---------------------------------------------------------
    # EFFECTIVE ACTIVE STATE (DAW LOGIC)
    # ---------------------------------------------------------
    def is_effectively_active(self, track_id: int) -> bool:
        tid = self._clamp(track_id)
        if tid is None:
            return False

        if self.is_muted(tid):
            return False

        if self.solo_mode_active():
            return self.is_solo(tid)

        return True

    # ---------------------------------------------------------
    # RECORD ARM
    # ---------------------------------------------------------
    def toggle_record_arm(self, track_id: int):
        tid = self._clamp(track_id)
        if tid:
            self.record_arm[tid] = not self.record_arm[tid]

    def set_record_arm(self, track_id: int, state: bool):
        tid = self._clamp(track_id)
        if tid:
            self.record_arm[tid] = bool(state)

    def is_record_armed(self, track_id: int) -> bool:
        tid = self._clamp(track_id)
        return self.record_arm.get(tid, False)

    # ---------------------------------------------------------
    # VOLUME / PAN
    # ---------------------------------------------------------
    def set_volume(self, track_id: int, volume: float):
        tid = self._clamp(track_id)
        if tid:
            try:
                volume = float(volume)
            except Exception:
                return
            self.volume[tid] = max(0.0, min(1.0, volume))

    def get_volume(self, track_id: int) -> float:
        tid = self._clamp(track_id)
        return self.volume.get(tid, 1.0)

    def set_pan(self, track_id: int, pan: float):
        tid = self._clamp(track_id)
        if tid:
            try:
                pan = float(pan)
            except Exception:
                return
            self.pan[tid] = max(-1.0, min(1.0, pan))

    def get_pan(self, track_id: int) -> float:
        tid = self._clamp(track_id)
        return self.pan.get(tid, 0.0)

    # ---------------------------------------------------------
    # REAL-TIME ACTIVITY
    # ---------------------------------------------------------
    def update_activity(self, track_id: int, level: float):
        tid = self._clamp(track_id)
        if tid is None:
            return

        try:
            level = float(level)
        except Exception:
            return

        self.activity[tid] = max(0.0, min(1.0, level))

    def get_activity(self, track_id: int) -> float:
        tid = self._clamp(track_id)
        return self.activity.get(tid, 0.0)

    # ---------------------------------------------------------
    # APPLY TO MIDI ENGINE
    # ---------------------------------------------------------
    def apply_midi_transform(self, track_id: int, note: int, velocity: int) -> Optional[Tuple[int, int]]:
        tid = self._clamp(track_id)
        if tid is None:
            return None

        if not self.is_effectively_active(tid):
            return None

        vol = self.get_volume(tid)
        velocity = int(velocity * vol)

        if velocity < 1:
            return None

        return note, velocity

    # ---------------------------------------------------------
    # NO-OP API (pre UIManager kompatibilitu)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return
