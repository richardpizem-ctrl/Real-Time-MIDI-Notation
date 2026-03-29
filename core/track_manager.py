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
        if not isinstance(track_id, int):
            return
        if track_id in self.track_visibility:
            self.track_visibility[track_id] = bool(visible)

    def toggle(self, track_id: int):
        if not isinstance(track_id, int):
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
        except Exception:
            return []

    # ---------------------------------------------------------
    # FARBY (BERIEME Z TrackSystem)
    # ---------------------------------------------------------
    def get_color(self, track_id: int) -> Tuple[int, int, int]:
        try:
            color = self.track_system.get_track_color(track_id)
            if (
                isinstance(color, (tuple, list)) and
                len(color) == 3 and
                all(isinstance(c, int) for c in color)
            ):
                return tuple(color)
        except Exception:
            pass

        return (255, 255, 255)

    # ---------------------------------------------------------
    # NÁZVY (BERIEME Z TrackSystem)
    # ---------------------------------------------------------
    def get_name(self, track_id: int) -> str:
        try:
            name = self.track_system.get_track_name(track_id)
            if isinstance(name, str) and name.strip():
                return name
        except Exception:
            pass

        return f"Track {track_id}"

    # ---------------------------------------------------------
    # AKTÍVNY TRACK (BERIEME Z TrackSystem)
    # ---------------------------------------------------------
    def get_active_track(self) -> Optional[int]:
        try:
            active = self.track_system.get_active_track()
            if active and hasattr(active, "id"):
                return active.id
        except Exception:
            pass
        return None

    # ---------------------------------------------------------
    # PRE RENDERER – KOMPLETNÉ INFO O STOPÁCH
    # ---------------------------------------------------------
    def get_renderer_track_info(self) -> Dict[int, Dict]:
        """
        Renderer dostane:
        - name
        - color
        - visible
        - enabled (z TrackSystem)
        - channel
        - is_active
        """
        info = {}

        try:
            tracks = getattr(self.track_system, "tracks", {})
        except Exception:
            tracks = {}

        if not isinstance(tracks, dict):
            return info

        active_id = self.get_active_track()

        for track_id, track in tracks.items():
            try:
                name = getattr(track, "name", f"Track {track_id}")
                color = getattr(track, "color", (255, 255, 255))
                enabled = getattr(track, "enabled", True)
                channel = getattr(track, "channel", track_id - 1)

                if not (
                    isinstance(color, (tuple, list)) and
                    len(color) == 3 and
                    all(isinstance(c, int) for c in color)
                ):
                    color = (255, 255, 255)

                info[track_id] = {
                    "name": name,
                    "color": color,
                    "visible": self.track_visibility.get(track_id, True),
                    "enabled": enabled,
                    "channel": channel,
                    "is_active": (track_id == active_id),
                }

            except Exception:
                info[track_id] = {
                    "name": f"Track {track_id}",
                    "color": (255, 255, 255),
                    "visible": True,
                    "enabled": True,
                    "channel": track_id - 1,
                    "is_active": False,
                }

        return info
