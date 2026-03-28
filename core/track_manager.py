"""
TrackManager – vizuálna vrstva pre renderer a UI.
Prepája sa priamo s TrackSystem (16 MIDI kanálov).
"""

from typing import Dict, Tuple, Optional, List
from core.track_manager import TrackSystem  # existujúci TrackSystem


class TrackManager:
    """
    TrackManager je vizuálna nadstavba nad TrackSystem.
    - Renderer zisťuje farby stôp
    - Renderer zisťuje viditeľnosť stôp
    - UI zisťuje názvy a aktívnu stopu
    """

    def __init__(self, track_system: TrackSystem):
        self.track_system = track_system

        # Viditeľnosť stôp pre renderer (nezávislá od MIDI enabled)
        self.track_visibility: Dict[int, bool] = {
            i: True for i in range(1, 17)
        }

    # ---------------------------------------------------------
    # VIDITEĽNOSŤ PRE RENDERER
    # ---------------------------------------------------------
    def set_visible(self, track_id: int, visible: bool):
        if track_id in self.track_visibility:
            self.track_visibility[track_id] = bool(visible)

    def toggle(self, track_id: int):
        if track_id in self.track_visibility:
            self.track_visibility[track_id] = not self.track_visibility[track_id]

    def is_visible(self, track_id: int) -> bool:
        return self.track_visibility.get(track_id, True)

    def get_visible_tracks(self) -> List[int]:
        return [tid for tid, v in self.track_visibility.items() if v]

    # ---------------------------------------------------------
    # FARBY (BERIEME Z TrackSystem)
    # ---------------------------------------------------------
    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        color = self.track_system.get_track_color(track_id)
        return color if color else (255, 255, 255)

    # ---------------------------------------------------------
    # NÁZVY (BERIEME Z TrackSystem)
    # ---------------------------------------------------------
    def get_name(self, track_id: int) -> str:
        name = self.track_system.get_track_name(track_id)
        return name if name else f"Track {track_id}"

    # ---------------------------------------------------------
    # AKTÍVNY TRACK (BERIEME Z TrackSystem)
    # ---------------------------------------------------------
    def get_active_track(self) -> Optional[int]:
        active = self.track_system.get_active_track()
        return active.id if active else None

    # ---------------------------------------------------------
    # PRE RENDERER – KOMPLETNÉ INFO O STOPS
    # ---------------------------------------------------------
    def get_renderer_track_info(self) -> Dict[int, Dict]:
        """
        Renderer dostane:
        - name
        - color
        - visible
        - enabled (z TrackSystem)
        - channel
        """
        info = {}
        for track_id, track in self.track_system.tracks.items():
            info[track_id] = {
                "name": track.name,
                "color": track.color,
                "visible": self.track_visibility.get(track_id, True),
                "enabled": track.enabled,
                "channel": track.channel,
                "is_active": (track_id == self.get_active_track()),
            }
        return info
