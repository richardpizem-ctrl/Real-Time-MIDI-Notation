# Layout engine – full staff layout, spacing and line breaking

from ..core.logger import Logger
from .drum_notation import annotate_drum_timeline   # 🔥 DOPLNENÉ

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
        line_height=150,              # vertikálny posun medzi riadkami
        min_bars_for_justify=2,       # No justify on short lines (< 2 bars)
        min_bars_for_smart_justify=3  # Smart Justify 2.0 až od 3 barov
    ):
        self.max_symbols_per_line = max_symbols_per_line
        self.min_spacing = min_spacing
        self.max_spacing = max_spacing
        self.barline_spacing = barline_spacing
        self.line_break_on_bars = line_break_on_bars

        self.max_line_width = max_line_width
        self.line_height = line_height

        self.min_bars_for_justify = min_bars_for_justify
        self.min_bars_for_smart_justify = min_bars_for_smart_justify


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
    # 3) SMART JUSTIFY 2.0 + CENTER LAST LINE + NO JUSTIFY ON SHORT LINES
    # ------------------------

    def _apply_spacing(self, lines):
        laid_out_lines = []
        last_line_index = len(lines) - 1
        line_index = 0

        for line in lines:

            # Rozdeliť symboly do taktov
            bars = []
            current_bar = []
            for sym in line:
                current_bar.append(sym)
                if sym.get("type") == "barline":
                    bars.append(current_bar)
                    current_bar = []
            if current_bar:
                bars.append(current_bar)

            bar_count = len(bars)

            # Šírka každého taktu (geometrická)
            bar_widths = [sum(self._spacing_for_symbol(s) for s in bar) for bar in bars]
            total_original_width = sum(bar_widths)

            # Rytmická váha každého taktu (Smart Justify 2.0)
            bar_rhythm_weights = []
            for bar in bars:
                weight = 0.0
                for s in bar:
                    if s.get("type") == "barline":
                        continue
                    dur = s.get("duration", 0.25)
                    if dur >= 1.0:
                        weight += 4.0 * dur
                    elif dur >= 0.5:
                        weight += 2.0 * dur
                    elif dur >= 0.25:
                        weight += 1.0 * dur
                    elif dur >= 0.125:
                        weight += 0.5 * dur
                    else:
                        weight += 0.25 * dur
                bar_rhythm_weights.append(weight or 1.0)

            Logger.info(
                f"Line {line_index}: bars={bar_count}, "
                f"width={total_original_width:.2f}, "
                f"rhythm_weights={bar_rhythm_weights}"
            )

            # CENTER LAST LINE
            if line_index == last_line_index:
                x_pos = (self.config.max_line_width - total_original_width) / 2
                laid_out_line = []

                for bar_idx, bar in enumerate(bars):
                    for sym in bar:
                        spacing = self._spacing_for_symbol(sym)

                        laid_out_line.append({
                            "symbol": sym,
                            "x": x_pos,
                            "line": line_index,
                            "spacing": spacing,
                            "debug": {
                                "mode": "center_last_line",
                                "bar_index": bar_idx,
                                "base_spacing": spacing,
                                "extra_spacing": 0.0,
                            },
                        })

                        x_pos += spacing

                laid_out_lines.append(laid_out_line)
                line_index += 1
                continue

            # NO JUSTIFY ON SHORT LINES
            if bar_count < self.config.min_bars_for_justify:
                laid_out_line = []
                x_pos = 0
                for bar_idx, bar in enumerate(bars):
                    for sym in bar:
                        spacing = self._spacing_for_symbol(sym)
                        laid_out_line.append({
                            "symbol": sym,
                            "x": x_pos,
                            "line": line_index,
                            "spacing": spacing,
                            "debug": {
                                "mode": "no_justify_short_line",
                                "bar_index": bar_idx,
                                "base_spacing": spacing,
                                "extra_spacing": 0.0,
                            },
                        })
                        x_pos += spacing

                laid_out_lines.append(laid_out_line)
                line_index += 1
                continue

            # JUSTIFY / SMART JUSTIFY 2.0
            remaining = max(self.config.max_line_width - total_original_width, 0)

            if bar_count >= self.config.min_bars_for_smart_justify:
                total_weight = sum(bar_rhythm_weights) or 1.0
                bar_extra = [
                    remaining * (rw / total_weight)
                    for rw in bar_rhythm_weights
                ]
                mode = "smart_justify_2_0"
            else:
                total_bar_weight = sum(bar_widths) or 1.0
                bar_extra = [
                    remaining * (bw / total_bar_weight)
                    for bw in bar_widths
                ]
                mode = "justify_width_based"

            laid_out_line = []
            x_pos = 0

            for bar_idx, (bar, extra_width) in enumerate(zip(bars, bar_extra)):

                gaps = max(len(bar) - 1, 1)
                extra_per_symbol = extra_width / gaps

                for i, sym in enumerate(bar):
                    base_spacing = self._spacing_for_symbol(sym)

                    if i < len(bar) - 1:
                        spacing = base_spacing + extra_per_symbol
                        extra = extra_per_symbol
                    else:
                        spacing = base_spacing
                        extra = 0.0

                    laid_out_line.append({
                        "symbol": sym,
                        "x": x_pos,
                        "line": line_index,
                        "spacing": spacing,
                        "debug": {
                            "mode": mode,
                            "bar_index": bar_idx,
                            "base_spacing": base_spacing,
                            "extra_spacing": extra,
                        },
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
        # 🔥 DOPLNENÉ — anotácia bicích
        timeline = annotate_drum_timeline(timeline)
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
