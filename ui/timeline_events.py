# =========================================================
# timeline_events.py – v2.0.0
# Stabilný event systém pre Timeline UI
# =========================================================

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, Callable, Dict, Any


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

@dataclass(slots=True)
class TimelineEvent:
    """
    Generic event object passed between UI and controller.
    V2.0.0 – stabilné, rýchle, typovo bezpečné.
    """
    event_type: TimelineEventType
    position: Optional[Tuple[int, int]] = None   # (x, y) in timeline coordinates
    delta: Optional[Tuple[int, int]] = None      # movement delta for drag/scroll
    marker_id: Optional[int] = None              # affected marker
    text: Optional[str] = None                   # rename text, etc.
    zoom_factor: Optional[float] = None          # zoom in/out
    raw_event: Optional[Any] = None              # original UI event (mouse, key, etc.)


# ------------------------------------------------------------
# EVENT DISPATCHER
# ------------------------------------------------------------

class TimelineEventDispatcher:
    """
    Central dispatcher for timeline events.
    timeline_ui.py → TimelineEventDispatcher → timeline_controller.py

    V2.0.0:
        - rýchlejší dispatch (predpočítaná tabuľka)
        - bezpečné volanie handlerov
        - žiadne if‑elif reťazce
        - pripravené na v3 (gesture events, multi-touch)
    """

    def __init__(self, controller: Any):
        self.controller = controller

        # Pre‑computed dispatch table (najrýchlejší spôsob)
        self._handlers: Dict[TimelineEventType, Callable[[TimelineEvent], None]] = {
            TimelineEventType.CLICK: controller.on_click,
            TimelineEventType.DOUBLE_CLICK: controller.on_double_click,
            TimelineEventType.DRAG_START: controller.on_drag_start,
            TimelineEventType.DRAG_MOVE: controller.on_drag_move,
            TimelineEventType.DRAG_END: controller.on_drag_end,
            TimelineEventType.MARKER_ADD: controller.on_marker_add,
            TimelineEventType.MARKER_DELETE: controller.on_marker_delete,
            TimelineEventType.MARKER_MOVE: controller.on_marker_move,
            TimelineEventType.MARKER_RENAME: controller.on_marker_rename,
            TimelineEventType.ZOOM: controller.on_zoom,
            TimelineEventType.SCROLL: controller.on_scroll,
        }

    def dispatch(self, event: TimelineEvent):
        """Route event to the correct controller method."""
        handler = self._handlers.get(event.event_type)

        if handler is None:
            print(f"[TimelineEventDispatcher] Unknown event: {event.event_type}")
            return

        try:
            handler(event)
        except Exception as e:
            print(f"[TimelineEventDispatcher] Handler error for {event.event_type}: {e}")
