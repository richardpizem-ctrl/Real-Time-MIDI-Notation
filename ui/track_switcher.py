"""
ui_track_switcher.py
Logical controller for switching between 16 MIDI tracks.

This module handles:
- track selection logic
- communication with TrackSelectionController
- optional visibility toggling (if UI wants it)
- callback system for UI layer (track_switcher_ui.py)
"""

from dataclasses import dataclass
from typing import Optional, Callable, Dict


@dataclass
class TrackSwitchEvent:
    track_id: int
    is_active: bool
    raw_event: Optional[object] = None


class TrackSwitcherLogic:
    """
    Pure logic layer for track switching.
    Does NOT draw anything — drawing is handled by track_switcher_ui.py.
    """

    def __init__(self, selection_controller, visibility_controller=None, color_map=None):
        self.selection_controller = selection_controller
        self.visibility_controller = visibility_controller
        self.color_map = color_map

        # UI callbacks for each track button
        self._callbacks: Dict[int, Callable[[TrackSwitchEvent], None]] = {}

    # ------------------------------------------------------------
    # CALLBACK REGISTRATION
    # ------------------------------------------------------------
    def register_callback(self, track_id: int, callback: Callable[[TrackSwitchEvent], None]):
        """Register UI callback for a specific track button."""
        self._callbacks[track_id] = callback

    # ------------------------------------------------------------
    # EVENT HANDLING
    # ------------------------------------------------------------
    def on_track_clicked(self, track_id: int, raw_event=None):
        """
        Handle logical track switching.
        Selecting a track does NOT toggle visibility.
        """

        # 1) Set active track
        self.selection_controller.select(track_id)
        is_active = (self.selection_controller.get_active_track() == track_id)

        # 2) Notify UI
        event = TrackSwitchEvent(track_id=track_id, is_active=is_active, raw_event=raw_event)

        callback = self._callbacks.get(track_id)
        if callback:
            try:
                callback(event)
            except Exception:
                pass

        print(f"[TrackSwitcherLogic] Track {track_id} selected (active={is_active})")

    # ------------------------------------------------------------
    # COLOR ACCESS
    # ------------------------------------------------------------
    def get_track_color(self, track_id: int):
        """Return the assigned color for the track."""
        if self.color_map is None:
            return "#FFFFFF"
        try:
            return self.color_map.get_color(track_id)
        except Exception:
            return "#FFFFFF"
