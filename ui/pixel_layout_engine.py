# =========================================================
# PixelLayoutEngine v4.3.0
# Ultra‑deterministický layout engine pre UI panely
# Hybrid upgrade: v4.0.0 → v4.3.0
# =========================================================

import dataclasses
from typing import Dict


@dataclasses.dataclass(slots=True)
class Rect:
    x: int
    y: int
    w: int
    h: int


class PixelLayoutEngine:
    """
    PixelLayoutEngine (v4.3.0)
    --------------------------
    Centrálne miesto pre výpočet layoutu UI podľa veľkosti okna.

    Vylepšenia v4.3.0:
        - ultra‑deterministický výpočet (bez driftu)
        - ochrana proti negatívnym hodnotám
        - auto‑resize pre renderer
        - pripravené pre dynamické panely v5 (collapsible, floating)
        - stabilné pri extrémnych rozmeroch okna
        - rýchlejšie výpočty (bez opakovaných max/min)
    """

    __slots__ = (
        "transport_height",
        "timeline_height",
        "track_switcher_height",
        "track_selector_height",
        "piano_height",
        "piano_roll_height",
        "staff_height",
        "visualizer_height",
        "inspector_width",
        "margin",
    )

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
    # MAIN LAYOUT COMPUTATION (v4.3.0)
    # ---------------------------------------------------------
    def compute_layout(self, window_width: int, window_height: int) -> Dict[str, Rect]:
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

        # hlavná šírka (bez inspector panelu)
        w_main = ww - self.inspector_width - self.margin * 2
        if w_main < 0:
            w_main = 0

        layout: Dict[str, Rect] = {}

        # Helper pre rýchle pridávanie panelov
        def add_panel(name: str, height: int):
            nonlocal y
            h = max(0, height)
            layout[name] = Rect(x0, y, w_main, h)
            y += h

        # -----------------------------------------------------
        # PANELY (deterministický top‑down flow)
        # -----------------------------------------------------
        add_panel("transport", self.transport_height)
        add_panel("timeline", self.timeline_height)
        add_panel("track_switcher", self.track_switcher_height)
        add_panel("track_selector", self.track_selector_height)
        add_panel("piano", self.piano_height)
        add_panel("piano_roll", self.piano_roll_height)
        add_panel("staff", self.staff_height)
        add_panel("visualizer", self.visualizer_height)

        # -----------------------------------------------------
        # RENDERER (zvyšok priestoru, min 200 px)
        # -----------------------------------------------------
        remaining = wh - y - self.margin
        renderer_h = 200 if remaining < 200 else remaining

        layout["renderer"] = Rect(x0, y, w_main, renderer_h)

        # -----------------------------------------------------
        # TRACK INSPECTOR (pravý panel)
        # -----------------------------------------------------
        inspector_x = ww - self.inspector_width - self.margin
        inspector_h = wh - self.margin * 2
        if inspector_h < 0:
            inspector_h = 0

        layout["track_inspector"] = Rect(
            inspector_x,
            self.margin,
            self.inspector_width,
            inspector_h,
        )

        return layout
