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
        │ TRANSPORT (fixed height)                     │
        ├──────────────────────────────────────────────┤
        │ TIMELINE (fixed 100 px – stabilné UI)        │
        ├──────────────────────────────────────────────┤
        │ TRACK SWITCHER (fixed height)                │
        ├──────────────────────────────────────────────┤
        │ TRACK SELECTOR (fixed height)                │
        ├──────────────────────────────────────────────┤
        │ PIANO / PIANO ROLL / STAFF / VISUALIZER      │
        │ (stacked, fixed heights)                     │
        ├──────────────────────────────────────────────┤
        │ RENDERER (fills the rest, min 200 px)        │
        ├──────────────────────────────────────────────┤
        │ TRACK INSPECTOR (fixed width, right side)    │
        └──────────────────────────────────────────────┘
    """

    def __init__(
        self,
        transport_height: int = 50,
        timeline_height: int = 100,   # pevná výška timeline
        track_switcher_height: int = 60,
        track_selector_height: int = 60,
        piano_height: int = 180,
        piano_roll_height: int = 180,
        staff_height: int = 200,
        visualizer_height: int = 200,
        inspector_width: int = 260,
        margin: int = 0,
    ):
        self.transport_height = transport_height
        self.timeline_height = timeline_height
        self.track_switcher_height = track_switcher_height
        self.track_selector_height = track_selector_height
        self.piano_height = piano_height
        self.piano_roll_height = piano_roll_height
        self.staff_height = staff_height
        self.visualizer_height = visualizer_height
        self.inspector_width = inspector_width
        self.margin = margin

    # ---------------------------------------------------------
    # MAIN LAYOUT COMPUTATION
    # ---------------------------------------------------------
    def compute_layout(self, window_width: int, window_height: int):
        """
        Vráti dict s Rect pre každý UI panel.
        """

        x0 = self.margin
        y = self.margin
        w_main = window_width - self.inspector_width - self.margin * 2

        layout = {}

        # -----------------------------------------------------
        # TRANSPORT
        # -----------------------------------------------------
        layout["transport"] = Rect(
            x0, y, w_main, self.transport_height
        )
        y += self.transport_height

        # -----------------------------------------------------
        # TIMELINE (pevná výška 100 px)
        # -----------------------------------------------------
        layout["timeline"] = Rect(
            x0, y, w_main, self.timeline_height
        )
        y += self.timeline_height

        # -----------------------------------------------------
        # TRACK SWITCHER
        # -----------------------------------------------------
        layout["track_switcher"] = Rect(
            x0, y, w_main, self.track_switcher_height
        )
        y += self.track_switcher_height

        # -----------------------------------------------------
        # TRACK SELECTOR
        # -----------------------------------------------------
        layout["track_selector"] = Rect(
            x0, y, w_main, self.track_selector_height
        )
        y += self.track_selector_height

        # -----------------------------------------------------
        # PIANO
        # -----------------------------------------------------
        layout["piano"] = Rect(
            x0, y, w_main, self.piano_height
        )
        y += self.piano_height

        # -----------------------------------------------------
        # PIANO ROLL
        # -----------------------------------------------------
        layout["piano_roll"] = Rect(
            x0, y, w_main, self.piano_roll_height
        )
        y += self.piano_roll_height

        # -----------------------------------------------------
        # STAFF
        # -----------------------------------------------------
        layout["staff"] = Rect(
            x0, y, w_main, self.staff_height
        )
        y += self.staff_height

        # -----------------------------------------------------
        # VISUALIZER
        # -----------------------------------------------------
        layout["visualizer"] = Rect(
            x0, y, w_main, self.visualizer_height
        )
        y += self.visualizer_height

        # -----------------------------------------------------
        # RENDERER (fills remaining space, min 200 px)
        # -----------------------------------------------------
        remaining = window_height - y - self.margin
        renderer_h = max(200, remaining)

        layout["renderer"] = Rect(
            x0, y, w_main, renderer_h
        )

        # -----------------------------------------------------
        # TRACK INSPECTOR (right side)
        # -----------------------------------------------------
        layout["track_inspector"] = Rect(
            window_width - self.inspector_width - self.margin,
            self.margin,
            self.inspector_width,
            window_height - self.margin * 2,
        )

        return layout
