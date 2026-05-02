# =========================================================
# PixelLayoutEngine v2.0.0
# Stabilný, deterministický layout engine pre UI panely
# =========================================================

import dataclasses

# Základný pixel‑presný rect
@dataclasses.dataclass(slots=True)
class Rect:
    x: int
    y: int
    w: int
    h: int


class PixelLayoutEngine:
    """
    PixelLayoutEngine (v2.0.0)
    --------------------------
    Centrálne miesto pre výpočet layoutu UI podľa veľkosti okna.

    Tento engine je "single source of truth" pre všetky UI panely.
    Layout je deterministický, stabilný a pripravený na v3 (dynamic panels).
    """

    def __init__(
        self,
        transport_height: int = 50,
        timeline_height: int = 100,
        track_switcher_height: int = 60,
        track_selector_height: int = 60,
        piano_height: int = 180,
        piano_roll_height: int = 180,
        staff_height: int = 200,
        visualizer_height: int = 200,
        inspector_width: int = 260,
        margin: int = 0,
    ):
        # Fixné UI rozmery
        self.transport_height = int(transport_height)
        self.timeline_height = int(timeline_height)
        self.track_switcher_height = int(track_switcher_height)
        self.track_selector_height = int(track_selector_height)
        self.piano_height = int(piano_height)
        self.piano_roll_height = int(piano_roll_height)
        self.staff_height = int(staff_height)
        self.visualizer_height = int(visualizer_height)
        self.inspector_width = int(inspector_width)
        self.margin = int(margin)

    # ---------------------------------------------------------
    # MAIN LAYOUT COMPUTATION
    # ---------------------------------------------------------
    def compute_layout(self, window_width: int, window_height: int):
        """
        Vráti dict[str, Rect] pre každý UI panel.

        Top‑down flow:
            TRANSPORT
            TIMELINE
            TRACK SWITCHER
            TRACK SELECTOR
            PIANO
            PIANO ROLL
            STAFF
            VISUALIZER
            RENDERER (zvyšok)
            TRACK INSPECTOR (vpravo)
        """

        ww = max(0, int(window_width))
        wh = max(0, int(window_height))

        x0 = self.margin
        y = self.margin
        w_main = max(0, ww - self.inspector_width - self.margin * 2)

        layout: dict[str, Rect] = {}

        # -----------------------------------------------------
        # TRANSPORT
        # -----------------------------------------------------
        layout["transport"] = Rect(x0, y, w_main, self.transport_height)
        y += self.transport_height

        # -----------------------------------------------------
        # TIMELINE (pevná výška)
        # -----------------------------------------------------
        layout["timeline"] = Rect(x0, y, w_main, self.timeline_height)
        y += self.timeline_height

        # -----------------------------------------------------
        # TRACK SWITCHER
        # -----------------------------------------------------
        layout["track_switcher"] = Rect(x0, y, w_main, self.track_switcher_height)
        y += self.track_switcher_height

        # -----------------------------------------------------
        # TRACK SELECTOR
        # -----------------------------------------------------
        layout["track_selector"] = Rect(x0, y, w_main, self.track_selector_height)
        y += self.track_selector_height

        # -----------------------------------------------------
        # PIANO
        # -----------------------------------------------------
        layout["piano"] = Rect(x0, y, w_main, self.piano_height)
        y += self.piano_height

        # -----------------------------------------------------
        # PIANO ROLL
        # -----------------------------------------------------
        layout["piano_roll"] = Rect(x0, y, w_main, self.piano_roll_height)
        y += self.piano_roll_height

        # -----------------------------------------------------
        # STAFF
        # -----------------------------------------------------
        layout["staff"] = Rect(x0, y, w_main, self.staff_height)
        y += self.staff_height

        # -----------------------------------------------------
        # VISUALIZER
        # -----------------------------------------------------
        layout["visualizer"] = Rect(x0, y, w_main, self.visualizer_height)
        y += self.visualizer_height

        # -----------------------------------------------------
        # RENDERER (zvyšok priestoru, min 200 px)
        # -----------------------------------------------------
        remaining = wh - y - self.margin
        renderer_h = max(200, remaining)

        layout["renderer"] = Rect(x0, y, w_main, renderer_h)

        # -----------------------------------------------------
        # TRACK INSPECTOR (pravý panel)
        # -----------------------------------------------------
        layout["track_inspector"] = Rect(
            ww - self.inspector_width - self.margin,
            self.margin,
            self.inspector_width,
            max(0, wh - self.margin * 2),
        )

        return layout
