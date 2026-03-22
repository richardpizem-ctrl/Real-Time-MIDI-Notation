# Layout engine – full staff layout, spacing and line breaking

from ..core.logger import Logger


class LayoutConfig:
    """Configuration for layout behavior."""
    def __init__(
        self,
        max_symbols_per_line=32,
        min_spacing=1,
        max_spacing=4,
        barline_spacing=2,
        line_break_on_bars=True,
        max_line_width=1200,          # maximálna šírka riadku v pixeloch
        line_height=150               # vertikálny posun medzi riadkami
    ):
        self.max_symbols_per_line = max_symbols_per_line
        self.min_spacing = min_spacing
        self.max_spacing = max_spacing
        self.barline_spacing = barline_spacing
        self.line_break_on_bars = line_break_on_bars

        self.max_line_width = max_line_width
        self.line_height = line_height


class LayoutEngine:
    """
    Takes a sequence of notation symbols (notes, rests, barlines, etc.)
    and produces a line-based layout with spacing and bar grouping.
    """

    def __init__(self, config=None):
        self.config = config or LayoutConfig()
        Logger.info("LayoutEngine initialized with full layout configuration.")

    def layout(self, symbols):
        if not symbols:
            Logger.warning("LayoutEngine.layout called with empty symbol list.")
            return []

        try:
            bars = self._group_into_bars(symbols)
            lines = self._break_into_lines(bars)
            laid_out = self._apply_spacing(lines)

            Logger.info(f"LayoutEngine produced {len(laid_out)} lines.")
            return laid_out

        except Exception as e:
            Logger.error(f"LayoutEngine.layout error: {e}")
            return []

    # ------------------------
    # 1) Grouping into bars
    # ------------------------

    def _group_into_bars(self, symbols):
        bars = []
        current_bar = []

        for sym in symbols:
            current_bar.append(sym)
            if sym.get("type") == "barline":
                bars.append(current_bar)
                current_bar = []

        if current_bar:
            bars.append(current_bar)

        Logger.info(f"LayoutEngine: grouped into {len(bars)} bars.")
        return bars

    # ------------------------
    # 2) Line breaking (šírkové zalamovanie)
    # ------------------------

    def _break_into_lines(self, bars):
        lines = []
        current_line = []
        current_width = 0

        for bar in bars:
            bar_width = self._estimate_bar_width(bar)

            if current_width + bar_width > self.config.max_line_width and current_line:
                lines.append(current_line)
                current_line = []
                current_width = 0

            current_line.extend(bar)
            current_width += bar_width

        if current_line:
            lines.append(current_line)

        Logger.info(f"LayoutEngine: broken into {len(lines)} lines.")
        return lines

    def _estimate_bar_width(self, bar):
        return sum(self._spacing_for_symbol(sym) for sym in bar)

    # ------------------------
    # 3) SMART JUSTIFY (proporčné rozťahovanie taktov)
    # ------------------------

    def _apply_spacing(self, lines):
        laid_out_lines = []
        line_index = 0

        for line in lines:

            # 1) Rozdeliť symboly do taktov
            bars = []
            current_bar = []
            for sym in line:
                current_bar.append(sym)
                if sym.get("type") == "barline":
                    bars.append(current_bar)
                    current_bar = []
            if current_bar:
                bars.append(current_bar)

            # 2) Šírka každého taktu
            bar_widths = [sum(self._spacing_for_symbol(s) for s in bar) for bar in bars]
            total_original_width = sum(bar_widths)

            # 3) Koľko chýba do max_line_width
            remaining = max(self.config.max_line_width - total_original_width, 0)

            # 4) Váha taktov (väčší takt = viac priestoru)
            total_bar_weight = sum(bar_widths) or 1

            # 5) Extra šírka pre každý takt podľa jeho veľkosti
            bar_extra = [
                remaining * (bw / total_bar_weight)
                for bw in bar_widths
            ]

            # 6) Rozloženie symbolov s novým spacingom
            laid_out_line = []
            x_pos = 0

            for bar, extra_width in zip(bars, bar_extra):

                gaps = max(len(bar) - 1, 1)
                extra_per_symbol = extra_width / gaps

                for i, sym in enumerate(bar):
                    base_spacing = self._spacing_for_symbol(sym)

                    if i < len(bar) - 1:
                        spacing = base_spacing + extra_per_symbol
                    else:
                        spacing = base_spacing

                    laid_out_line.append({
                        "symbol": sym,
                        "x": x_pos,
                        "line": line_index,
                        "spacing": spacing,
                    })

                    x_pos += spacing

            laid_out_lines.append(laid_out_line)
            line_index += 1

        return laid_out_lines

    def _spacing_for_symbol(self, symbol):
        sym_type = symbol.get("type")
        duration = symbol.get("duration", 0.25)

        if sym_type == "barline":
            return self.config.barline_spacing

        base = duration * 8
        return max(self.config.min_spacing, min(self.config.max_spacing, base))


# -------------------------------------------------------------------------
# GRAFICKÝ LAYOUT PRE RENDERER (x/y pozície)
# -------------------------------------------------------------------------

class PixelLayoutEngine:
    def __init__(
        self,
        note_spacing: float = 40.0,
        measure_width: float = 480.0,
        staff_top: float = 80.0,
        staff_spacing: float = 140.0,
    ):
        self.note_spacing = note_spacing
        self.measure_width = measure_width
        self.staff_top = staff_top
        self.staff_spacing = staff_spacing

        self.track_offsets = {
            "melody": 0.0,
            "bass": staff_spacing,
            "drums": staff_spacing * 2,
            "chords": staff_spacing * 3,
        }

        self.drum_y_map = {
            36: +20,
            38: 0,
            42: -20,
            46: -20,
            49: -40,
            51: -40,
        }

        self.reference_pitch = 60
        self.pitch_step = 3.0

    def layout_timeline(self, timeline):
        return [self.layout_note(note) for note in timeline]

    def layout_single(self, note):
        return self.layout_note(note)

    def layout_note(self, note):
        return {
            **note,
            "x": self._compute_x(note),
            "y": self._compute_y(note),
        }

    def _compute_x(self, note):
        return note.get("start", 0.0) * self.note_spacing

    def _compute_y(self, note):
        pitch = note.get("pitch", self.reference_pitch)
        track_type = note.get("track_type", "melody")

        base_y = self._get_track_base_y(track_type)

        if track_type == "drums":
            return base_y + self.drum_y_map.get(pitch, 0)

        dy = (self.reference_pitch - pitch) * self.pitch_step
        return base_y + dy

    def _get_track_base_y(self, track_type):
        return self.staff_top + self.track_offsets.get(track_type, 0.0)
