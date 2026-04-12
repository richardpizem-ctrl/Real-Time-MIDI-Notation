import dataclasses


@dataclasses.dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int


class PixelLayoutEngine:
    """
    PixelLayoutEngine
    ------------------
    Centrálne miesto pre výpočet layoutu UI podľa veľkosti okna.

    Základný layout (DAW štýl):

        ┌──────────────────────────────────────────────┐
        │ TRACK SWITCHER (fixed height)                │
        ├──────────────────────────────────────────────┤
        │ TIMELINE (fixed/dynamic height)              │
        ├──────────────────────────────────────────────┤
        │ NOTATION RENDERER (fills the rest)           │
        └──────────────────────────────────────────────┘
    """

    def __init__(
        self,
        track_switcher_height: int = 60,
        timeline_min_height: int = 180,
        timeline_max_height: int = 260,
        margin: int = 0,
    ):
        self.track_switcher_height = track_switcher_height
        self.timeline_min_height = timeline_min_height
        self.timeline_max_height = timeline_max_height
        self.margin = margin

    def compute_layout(self, window_width: int, window_height: int) -> dict:
        """
        Vypočíta layout pre hlavné UI panely.

        Returns dict:
            {
                "track_switcher": Rect,
                "timeline": Rect,
                "renderer": Rect,
            }
        """

        x0 = self.margin
        y0 = self.margin
        w = max(0, window_width - 2 * self.margin)
        h = max(0, window_height - 2 * self.margin)

        # TRACK SWITCHER – fixná výška hore
        ts_h = min(max(self.track_switcher_height, 0), h)
        track_switcher = Rect(x0, y0, w, ts_h)

        # TIMELINE – medzi track switcherom a rendererom
        remaining_after_ts = max(0, h - ts_h)

        # timeline výška – snaží sa byť medzi min a max,
        # ale rešpektuje reálnu výšku okna
        tl_h = min(self.timeline_max_height, remaining_after_ts // 2)
        tl_h = max(self.timeline_min_height, tl_h)
        tl_h = min(tl_h, remaining_after_ts)

        timeline = Rect(x0, y0 + ts_h, w, tl_h)

        # RENDERER – všetko, čo ostane dole
        remaining_after_tl = max(0, remaining_after_ts - tl_h)
        renderer = Rect(x0, y0 + ts_h + tl_h, w, remaining_after_tl)

        return {
            "track_switcher": track_switcher,
            "timeline": timeline,
            "renderer": renderer,
        }

    def get_track_switcher_rect(self, window_width: int, window_height: int) -> Rect:
        return self.compute_layout(window_width, window_height)["track_switcher"]

    def get_timeline_rect(self, window_width: int, window_height: int) -> Rect:
        return self.compute_layout(window_width, window_height)["timeline"]

    def get_renderer_rect(self, window_width: int, window_height: int) -> Rect:
        return self.compute_layout(window_width, window_height)["renderer"]
