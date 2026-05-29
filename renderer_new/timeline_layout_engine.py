# =========================================================
# TimelineLayoutEngine v4.3.0
# Optimalizovaný engine pre prepočet pixelov na timeline
# - mikrooptimalizácie
# - real‑time safe
# - partial redraw friendly
# - diagnostické fallbacky
# =========================================================

from typing import Optional
from ..core.logger import Logger


class TimelineLayoutEngine:
    """
    TimelineLayoutEngine (v4.3.0)
    -----------------------------
    Účel:
        - Prepočítava pixely pre timeline (grid, playhead, eventy)
        - Riadi zoom, offset a škálovanie
        - Oddelené od renderovania pre čistú architektúru
        - Pripravené pre PixelLayoutEngine (v4)

    Vylepšenia v4.3.0:
        - optimalizované výpočty
        - bezpečné fallbacky
        - žiadne alokácie v slučke
        - real‑time safe
        - partial redraw kompatibilné
    """

    __slots__ = (
        "pixels_per_beat",
        "beats_per_bar",
        "zoom",
        "offset_x",
    )

    def __init__(
        self,
        pixels_per_beat: int = 100,
        beats_per_bar: int = 4
    ) -> None:

        try:
            self.pixels_per_beat = max(1, int(pixels_per_beat))
        except Exception:
            self.pixels_per_beat = 100

        try:
            self.beats_per_bar = max(1, int(beats_per_bar))
        except Exception:
            self.beats_per_bar = 4

        # View parameters
        self.zoom: float = 1.0
        self.offset_x: int = 0

        Logger.info("TimelineLayoutEngine initialized (v4.3.0).")

    # ---------------------------------------------------------
    # ZOOM CONTROL
    # ---------------------------------------------------------
    def set_zoom(self, zoom: float) -> None:
        """Nastaví zoom timeline."""
        try:
            z = float(zoom)
            if z < 0.1:
                z = 0.1
            elif z > 5.0:
                z = 5.0
            self.zoom = z
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine zoom error: {e}")

    # ---------------------------------------------------------
    # OFFSET CONTROL
    # ---------------------------------------------------------
    def set_offset(self, offset_x: float) -> None:
        """Nastaví horizontálny posun timeline."""
        try:
            self.offset_x = int(offset_x)
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine offset error: {e}")

    # ---------------------------------------------------------
    # PIXELS PER BEAT CONTROL
    # ---------------------------------------------------------
    def set_pixels_per_beat(self, ppb: int) -> None:
        """Externé nastavenie základného PPB."""
        try:
            self.pixels_per_beat = max(1, int(ppb))
        except Exception:
            Logger.error("TimelineLayoutEngine set_pixels_per_beat error.")

    def get_pixels_per_beat(self) -> int:
        """Vráti aktuálne PPB vrátane zoomu."""
        try:
            return int(self.pixels_per_beat * self.zoom)
        except Exception:
            return self.pixels_per_beat

    # ---------------------------------------------------------
    # BEATS → PIXELS
    # ---------------------------------------------------------
    def compute_x_position(self, beat_index: float) -> int:
        """
        Prepočíta beat index na pixelovú pozíciu.
        beat_index môže byť float (napr. 3.5 = pol beat).
        Real‑time safe.
        """
        try:
            base_px = beat_index * self.pixels_per_beat
            zoomed_px = base_px * self.zoom
            return int(zoomed_px - self.offset_x)
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine compute error: {e}")
            return 0

    # ---------------------------------------------------------
    # PIXELS → BEATS
    # ---------------------------------------------------------
    def compute_beat_from_x(self, x: int) -> float:
        """Prepočíta pixelovú pozíciu späť na beat index."""
        try:
            adjusted = (x + self.offset_x) / max(self.zoom, 0.0001)
            return adjusted / self.pixels_per_beat
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine reverse compute error: {e}")
            return 0.0

    # ---------------------------------------------------------
    # GENERICKÝ TIME → PIXELS (kompatibilita pre markery)
    # ---------------------------------------------------------
    def time_to_x(self, time_value: float) -> int:
        """Prepočet časovej hodnoty na X pozíciu."""
        try:
            return self.compute_x_position(float(time_value))
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine time_to_x error: {e}")
            return 0

    def x_to_time(self, x: int) -> float:
        """Inverzný prepočet X pozície na časovú hodnotu."""
        try:
            return self.compute_beat_from_x(x)
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine x_to_time error: {e}")
            return 0.0
