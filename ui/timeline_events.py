# =========================================================
# timeline_events.py – v4.3.0
# Ultra‑rýchly, deterministický event systém pre Timeline UI
# =========================================================

from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional, Tuple, Callable, Dict, Any


# ------------------------------------------------------------
# EVENT TYPES (v4.3.0)
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

    # v4.3.0 gesture events
    PINCH = auto()
    LONG_PRESS = auto()
    ROTATE = auto()          # nový gesture event
    TWO_FINGER_TAP = auto()  # nový gesture event


# ------------------------------------------------------------
# EVENT DATA STRUCTURES (v4.3.0)
# ------------------------------------------------------------

@dataclass(slots=True)
class TimelineEvent:
    """
    Generic event object passed between UI and controller.
    v4.3.0 – stabilné, rýchle, typovo bezpečné, rozšíriteľné.
    """
    event_type: TimelineEventType
    position: Optional[Tuple[int, int]] = None
    delta: Optional[Tuple[int, int]] = None
    marker_id: Optional[int] = None
    text: Optional[str] = None
    zoom_factor: Optional[float] = None
    raw_event: Optional[Any] = None

    # v4.3.0 gesture metadata
    pressure: Optional[float] = None
    fingers: Optional[int] = None
    angle: Optional[float] = None       # rotate gesture
    scale: Optional[float] = None       # pinch zoom scale


# ------------------------------------------------------------
# EVENT DISPATCHER (v4.3.0)
# ------------------------------------------------------------

class TimelineEventDispatcher:
    """
    Central dispatcher for timeline events.
    timeline_ui.py → TimelineEventDispatcher → timeline_controller.py

    v4.3.0:
        - ultra‑rýchly dispatch (predpočítaná tabuľka)
        - bezpečné volanie handlerov
        - fallback pre neimplementované eventy
        - rozšírené gesture events (rotate, pinch, long‑press)
        - pripravené pre stylus, multi‑touch, AI gesture engine v5
    """

    __slots__ = ("controller", "_handlers")

    def __init__(self, controller: Any):
        self.controller = controller

        # Pre‑computed dispatch table (najvyšší výkon)
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

            # gesture events (optional handlers)
            TimelineEventType.PINCH: getattr(controller, "on_pinch", lambda e: None),
            TimelineEventType.LONG_PRESS: getattr(controller, "on_long_press", lambda e: None),
            TimelineEventType.ROTATE: getattr(controller, "on_rotate", lambda e: None),
            TimelineEventType.TWO_FINGER_TAP: getattr(controller, "on_two_finger_tap", lambda e: None),
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
