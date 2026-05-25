# =========================================================
# TrackManager v4.1.0
# Stabilná CORE verzia pre Runtime 4.x–5.x
# =========================================================

from typing import Dict, Tuple, Optional
import threading

from core.logger import Logger
from core.event_types import (
    TRACK_SELECTED,
    TRACK_MUTED,
    TRACK_SOLOED,
    TRACK_COLOR_CHANGED,
    TRACK_NAME_CHANGED,
)


class TrackManager:
    """
    TrackManager v4.1.0:
    - thread-safe
    - čistý CORE modul
    - bez AI hookov
    - bez Engraving hookov
    - bez Real-Time pipeline
    """

    def __init__(self, track_system, event_bus=None):
        self.track_system = track_system
        self.event_bus = event_bus

        self._lock = threading.Lock()

        # Visibility
        self.track_visibility: Dict[int, bool] = {i: True for i in range(1, 17)}

        # Active track
        self.active_track: int = 1

        # Mute / Solo
        self.mute: Dict[int, bool] = {i: False for i in range(1, 17)}
        self.solo: Dict[int, bool] = {i: False for i in range(1, 17)}

        # Volume / Pan
        self.volume: Dict[int, float] = {i: 1.0 for i in range(1, 17)}
        self.pan: Dict[int, float] = {i: 0.0 for i in range(1, 17)}

        Logger.info("TrackManager initialized (v4.1.0).")

    # ---------------------------------------------------------
    # INTERNAL: CLAMP
    # ---------------------------------------------------------
    def _clamp(self, track_id: int) -> Optional[int]:
        try:
            tid = int(track_id)
        except Exception:
            return None
        return tid if 1 <= tid <= 16 else None

    # ---------------------------------------------------------
    # ACTIVE TRACK
    # ---------------------------------------------------------
    def set_active_track(self, track_id: int):
        tid = self._clamp(track_id)
        if tid is None:
            return

        with self._lock:
            self.active_track = tid

        if self.event_bus:
            self.event_bus.publish(TRACK_SELECTED, tid)

    # ---------------------------------------------------------
    # VISIBILITY
    # ---------------------------------------------------------
    def set_visible(self, track_id: int, visible: bool):
        tid = self._clamp(track_id)
        if tid is None:
            return

        with self._lock:
            self.track_visibility[tid] = bool(visible)

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
        except Exception:
            pass

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
        except Exception:
            pass

        return f"Track {tid}"

    # ---------------------------------------------------------
    # MUTE / SOLO
    # ---------------------------------------------------------
    def set_mute(self, track_id: int, state: bool):
        tid = self._clamp(track_id)
        if tid is None:
            return

        with self._lock:
            self.mute[tid] = bool(state)

        if self.event_bus:
            self.event_bus.publish(TRACK_MUTED, {"track": tid, "state": state})

    def set_solo(self, track_id: int, state: bool):
        tid = self._clamp(track_id)
        if tid is None:
            return

        with self._lock:
            self.solo[tid] = bool(state)

        if self.event_bus:
            self.event_bus.publish(TRACK_SOLOED, {"track": tid, "state": state})

    # ---------------------------------------------------------
    # EFFECTIVE ACTIVE STATE
    # ---------------------------------------------------------
    def is_effectively_active(self, track_id: int) -> bool:
        tid = self._clamp(track_id)
        if tid is None:
            return False

        if self.mute.get(tid):
            return False

        if any(self.solo.values()):
            return self.solo.get(tid, False)

        return True

    # ---------------------------------------------------------
    # VOLUME / PAN
    # ---------------------------------------------------------
    def set_volume(self, track_id: int, volume: float):
        tid = self._clamp(track_id)
        if tid:
            with self._lock:
                try:
                    volume = float(volume)
                except Exception:
                    return
                self.volume[tid] = max(0.0, min(1.0, volume))

    def set_pan(self, track_id: int, pan: float):
        tid = self._clamp(track_id)
        if tid:
            with self._lock:
                try:
                    pan = float(pan)
                except Exception:
                    return
                self.pan[tid] = max(-1.0, min(1.0, pan))

    # ---------------------------------------------------------
    # MIDI TRANSFORM (CORE SAFE)
    # ---------------------------------------------------------
    def apply_midi_transform(self, track_id: int, note: int, velocity: int):
        tid = self._clamp(track_id)
        if tid is None:
            return None

        if not self.is_effectively_active(tid):
            return None

        vol = self.volume.get(tid, 1.0)
        velocity = int(velocity * vol)

        if velocity < 1:
            return None

        return note, velocity

    # ---------------------------------------------------------
    # SHUTDOWN
    # ---------------------------------------------------------
    def shutdown(self):
        Logger.info("TrackManager shutdown.")
