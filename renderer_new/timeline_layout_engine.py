from typing import Optional
from ..core.logger import Logger


class TimelineLayoutEngine:
    """
    TimelineLayoutEngine (Rozloženie časovej osi)
    ---------------------------------------------
    FÁZA 4 – Stabilizovaná verzia

    Účel:
        - Prepočítava pixely pre timeline (grid, playhead, eventy)
        - Riadi zoom, offset a škálovanie
        - Oddelené od renderovania pre čistú architektúru
        - Pripravené pre PixelLayoutEngine

    Vlastnosti:
        - Real‑time safe
        - Žiadne blokujúce operácie
        - Jednoduché API: compute_x_position(), set_zoom(), set_offset()
    """

    def __init__(
        self,
        pixels_per_beat: int = 100,
        beats_per_bar: int = 4
    ) -> None:

        self.pixels_per_beat = pixels_per_beat
        self.beats_per_bar = beats_per_bar

        self.zoom: float = 1.0
        self.offset_x: int = 0  # posun timeline doľava/doprava

        Logger.info("TimelineLayoutEngine initialized.")

    # ---------------------------------------------------------
    # ZOOM CONTROL
    # ---------------------------------------------------------
    def set_zoom(self, zoom: float) -> None:
        """Nastaví zoom timeline (set timeline zoom)."""
        try:
            self.zoom = max(0.1, min(zoom, 5.0))  # bezpečné limity
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine zoom error: {e}")

    # ---------------------------------------------------------
    # OFFSET CONTROL
    # ---------------------------------------------------------
    def set_offset(self, offset_x: int) -> None:
        """Nastaví horizontálny posun timeline (set timeline offset)."""
        try:
            self.offset_x = offset_x
        except Exception as e:
            Logger.error(f"TimelineLayoutEngine offset error: {e}")

    # ---------------------------------------------------------
    # PIXEL POSITION CALCULATION
    # ---------------------------------------------------------
    def compute_x_position(self, beat_index: float) -> int:
        """
        Prepočíta beat index na pixelovú pozíciu (compute pixel position).
        beat_index môže byť float (napr. 3.5 = pol beat).
        """
        try:
            base_px = beat_index * self.pixels_per_beat
            zoomed_px = base_px * self.zoom
            final_px = int(zoomed_px + self.offset_x)
            return final_px

        except Exception as e:
            Logger.error(f"TimelineLayoutEngine compute error: {e}")
            return 0

    # ---------------------------------------------------------
    # REVERSE CALCULATION (PIXELS → BEATS)
    # ---------------------------------------------------------
    def compute_beat_from_x(self, x: int) -> float:
        """
        Prepočíta pixelovú pozíciu späť na beat index (reverse mapping).
        """
        try:
            adjusted = (x - self.offset_x) / max(self.zoom, 0.0001)
            beat = adjusted / self.pixels_per_beat
            return beat

        except Exception as e:
            Logger.error(f"TimelineLayoutEngine reverse compute error: {e}")
            return 0.0

