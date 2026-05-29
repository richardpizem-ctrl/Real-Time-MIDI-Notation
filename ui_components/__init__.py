# =========================================================
# ui_components/__init__.py v4.3.0
# Central registry for UI components (v4.3 architecture)
# =========================================================

from .transport_ui import TransportUI
from .track_selection_controller import TrackSelectionController
from .track_visibility_controller import TrackVisibilityController
from .track_color_map import TrackColorMap
from .track_control_manager import TrackControlManager

from .track_selector_ui import TrackSelectorUI
from .track_switcher_ui import TrackSwitcherUI

from .timeline_ui import TimelineUI
from .staff_ui import StaffUI
from .piano_roll_ui import PianoRollUI
from .piano_keyboard_ui import PianoKeyboardUI


__all__ = [
    "TransportUI",
    "TrackSelectionController",
    "TrackVisibilityController",
    "TrackColorMap",
    "TrackControlManager",
    "TrackSelectorUI",
    "TrackSwitcherUI",
    "TimelineUI",
    "StaffUI",
    "PianoRollUI",
    "PianoKeyboardUI",
]


def create_default_ui_components(track_system=None, notation_processor=None):
    """
    Factory for default v4.3 UI component set.

    Returns a dict with pre-instantiated components.
    This keeps UIWindow / UIManager wiring clean and explicit.
    """

    # Core controllers
    selection = TrackSelectionController()
    visibility = TrackVisibilityController()
    colors = TrackColorMap()
    control = TrackControlManager()

    # UI components
    return {
        "transport": TransportUI(),
        "track_selection": selection,
        "track_visibility": visibility,
        "track_colors": colors,
        "track_control": control,

        # Visual UI
        "track_selector": TrackSelectorUI(control, 1400, 40),
        "track_switcher": TrackSwitcherUI(
            0, 0, 1400, 120,
            track_colors=colors.colors_hex,
            event_bus=track_system if track_system else None,
            track_control_manager=control,
        ),

        "timeline": TimelineUI(),
        "staff": StaffUI(),
        "piano_roll": PianoRollUI(),
        "piano_keyboard": PianoKeyboardUI(),
    }
