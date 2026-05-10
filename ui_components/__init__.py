# =========================================================
# ui_components/__init__.py v4.0.0
# Central registry for UI components (v4 architecture)
# =========================================================

from .transport_ui import TransportUI
from .track_selection_controller import TrackSelectionController
# from .track_visibility_controller import TrackVisibilityController
# from .track_color_map import TrackColorMap
# from .track_control_panel import TrackControlPanel
# from .timeline_ui import TimelineUI
# from .staff_ui import StaffUI
# from .piano_roll_ui import PianoRollUI
# from .piano_keyboard_ui import PianoKeyboardUI


__all__ = [
    "TransportUI",
    "TrackSelectionController",
    # "TrackVisibilityController",
    # "TrackColorMap",
    # "TrackControlPanel",
    # "TimelineUI",
    # "StaffUI",
    # "PianoRollUI",
    # "PianoKeyboardUI",
]


def create_default_ui_components():
    """
    Factory for default v4 UI component set.

    Returns a dict with pre-instantiated components.
    This keeps UIWindow / UIManager wiring clean and explicit.
    """
    return {
        "transport": TransportUI(),
        "track_selection": TrackSelectionController(),
        # "track_visibility": TrackVisibilityController(),
        # "track_colors": TrackColorMap(),
        # "track_control": TrackControlPanel(),
        # "timeline": TimelineUI(),
        # "staff": StaffUI(),
        # "piano_roll": PianoRollUI(),
        # "piano_keyboard": PianoKeyboardUI(),
    }

