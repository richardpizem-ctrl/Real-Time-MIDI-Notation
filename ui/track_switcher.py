"""
ui_track_switcher.py
Logical controller for switching between 16 MIDI tracks.

This module handles:
- track selection logic
- track activation/deactivation
- communication with TrackSelectionController and TrackVisibilityController
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

    def __init__(self, selection_controller, visibility_controller, color_map):
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
        """Handle logical track switching."""
        is_active = self.selection_controller.toggle_track(track_id)

        # update visibility
        self.visibility_controller.set_track_visible(track_id, is_active)

        # notify UI
        event = TrackSwitchEvent(track_id=track_id, is_active=is_active, raw_event=raw_event)

        if track_id in self._callbacks:
            self._callbacks[track_id](event)

        print(f"[TrackSwitcherLogic] Track {track_id} active={is_active}")

    # ------------------------------------------------------------
    # COLOR ACCESS
    # ------------------------------------------------------------
    def get_track_color(self, track_id: int):
        """Return the assigned color for the track."""
        return self.color_map.get_color(track_id)
