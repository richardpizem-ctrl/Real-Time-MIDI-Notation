import dataclasses

# Basic rectangle used for pixel‑precise UI layout
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

    Tento engine je "single source of truth" pre všetky UI panely.
    Každý panel dostane presné pixely (x, y, w, h) podľa aktuálnej
    veľkosti okna. Layout je navrhnutý v štýle DAW aplikácií:

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
        # All fixed UI dimensions
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

        Tento výpočet prebieha zhora nadol (top‑down flow):
        - najprv transport
        - potom timeline
        - potom track switcher a track selector
        - potom stacked panely (piano, piano roll, staff, visualizer)
        - renderer dostane zvyšok priestoru (min 200 px)
        - track inspector je vždy vpravo, na celú výšku
        """

        x0 = self.margin
        y = self.margin
        w_main = window_width - self.inspector_width - self.margin * 2

        layout = {}

        # -----------------------------------------------------
        # TRANSPORT (top bar)
        # -----------------------------------------------------
        layout["transport"] = Rect(
            x0, y, w_main, self.transport_height
        )
        y += self.transport_height

        # -----------------------------------------------------
        # TIMELINE (pevná výška 100 px)
        # Stabilný prvok UI – nemá sa meniť pri resize.
        # -----------------------------------------------------
        layout["timeline"] = Rect(
            x0, y, w_main, self.timeline_height
        )
        y += self.timeline_height

        # -----------------------------------------------------
        # TRACK SWITCHER (prepínanie trackov)
        # -----------------------------------------------------
        layout["track_switcher"] = Rect(
            x0, y, w_main, self.track_switcher_height
        )
        y += self.track_switcher_height

        # -----------------------------------------------------
        # TRACK SELECTOR (výber aktuálneho tracku)
        # -----------------------------------------------------
        layout["track_selector"] = Rect(
            x0, y, w_main, self.track_selector_height
        )
        y += self.track_selector_height

        # -----------------------------------------------------
        # PIANO (klaviatúra)
        # -----------------------------------------------------
        layout["piano"] = Rect(
            x0, y, w_main, self.piano_height
        )
        y += self.piano_height

        # -----------------------------------------------------
        # PIANO ROLL (MIDI grid)
        # -----------------------------------------------------
        layout["piano_roll"] = Rect(
            x0, y, w_main, self.piano_roll_height
        )
        y += self.piano_roll_height

        # -----------------------------------------------------
        # STAFF (notová osnova)
        # -----------------------------------------------------
        layout["staff"] = Rect(
            x0, y, w_main, self.staff_height
        )
        y += self.staff_height

        # -----------------------------------------------------
        # VISUALIZER (grafické zobrazenie MIDI)
        # -----------------------------------------------------
        layout["visualizer"] = Rect(
            x0, y, w_main, self.visualizer_height
        )
        y += self.visualizer_height

        # -----------------------------------------------------
        # RENDERER (fills remaining space, min 200 px)
        # Hlavná plocha pre vykresľovanie notácie.
        # -----------------------------------------------------
        remaining = window_height - y - self.margin
        renderer_h = max(200, remaining)

        layout["renderer"] = Rect(
            x0, y, w_main, renderer_h
        )

        # -----------------------------------------------------
        # TRACK INSPECTOR (right side panel)
        # Fixná šírka, siaha odhora až nadol.
        # -----------------------------------------------------
        layout["track_inspector"] = Rect(
            window_width - self.inspector_width - self.margin,
            self.margin,
            self.inspector_width,
            window_height - self.margin * 2,
        )

        return layout
