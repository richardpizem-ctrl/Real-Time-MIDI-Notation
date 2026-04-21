"""
timeline_events.py
Event handling module for the Timeline UI.

This module defines all event types and event dispatching logic
used by timeline_ui.py, timeline_controller.py and timeline_renderer.py.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple


# ------------------------------------------------------------
# EVENT TYPES
# ------------------------------------------------------------

class TimelineEventType(Enum):
    CLICK = auto()
    DOUBLE_CLICK = auto()
    DRAG_START = auto()
    DRAG_MOVE = auto()
    DRAG_END = auto()
    MARKER_ADD = auto()
    MARKER_DELETE = auto()
    MARKER_MOVE = auto()
    MARKER_RENAME = auto()
    ZOOM = auto()
    SCROLL = auto()


# ------------------------------------------------------------
# EVENT DATA STRUCTURES
# ------------------------------------------------------------

@dataclass
class TimelineEvent:
    """Generic event object passed between UI and controller."""
    event_type: TimelineEventType
    position: Optional[Tuple[int, int]] = None   # (x, y) in timeline coordinates
    delta: Optional[Tuple[int, int]] = None      # movement delta for drag/scroll
    marker_id: Optional[int] = None              # affected marker
    text: Optional[str] = None                   # rename text, etc.
    zoom_factor: Optional[float] = None          # zoom in/out
    raw_event: Optional[object] = None           # original UI event (mouse, key, etc.)


# ------------------------------------------------------------
# EVENT DISPATCHER
# ------------------------------------------------------------

class TimelineEventDispatcher:
    """
    Central dispatcher for timeline events.
    timeline_ui.py → TimelineEventDispatcher → timeline_controller.py
    """

    def __init__(self, controller):
        self.controller = controller

    def dispatch(self, event: TimelineEvent):
        """Route event to the correct controller method."""
        et = event.event_type

        if et == TimelineEventType.CLICK:
            self.controller.on_click(event)

        elif et == TimelineEventType.DOUBLE_CLICK:
            self.controller.on_double_click(event)

        elif et == TimelineEventType.DRAG_START:
            self.controller.on_drag_start(event)

        elif et == TimelineEventType.DRAG_MOVE:
            self.controller.on_drag_move(event)

        elif et == TimelineEventType.DRAG_END:
            self.controller.on_drag_end(event)

        elif et == TimelineEventType.MARKER_ADD:
            self.controller.on_marker_add(event)

        elif et == TimelineEventType.MARKER_DELETE:
            self.controller.on_marker_delete(event)

        elif et == TimelineEventType.MARKER_MOVE:
            self.controller.on_marker_move(event)

        elif et == TimelineEventType.MARKER_RENAME:
            self.controller.on_marker_rename(event)

        elif et == TimelineEventType.ZOOM:
            self.controller.on_zoom(event)

        elif et == TimelineEventType.SCROLL:
            self.controller.on_scroll(event)

        else:
            print(f"[TimelineEventDispatcher] Unknown event: {et}")
