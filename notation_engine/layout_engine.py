# =========================================================
# LayoutEngine v2.0.0
# Stabilný layout notácie pre Real-Time-MIDI-Notation
# =========================================================

from typing import List, Dict, Any
from ..core.logger import Logger
from .drum_notation import annotate_drum_timeline


class LayoutConfig:
    """Configuration for layout behavior."""

    def __init__(
        self,
        max_symbols_per_line: int = 32,
        min_spacing: float = 1.0,
        max_spacing: float = 4.0,
        barline_spacing: float = 2.0,
        line_break_on_bars: bool = True,
        max_line_width: float = 1200.0,
        line_height: float = 150.0,
        min_bars_for_justify: int = 2,
        min_bars_for_smart_justify: int = 3,
    ):
        self.max_symbols_per_line = int(max_symbols_per_line)
        self.min_spacing = float(min_spacing)
        self.max_spacing = float(max_spacing)
        self.barline_spacing = float(barline_spacing)
        self.line_break_on_bars = bool(line_break_on_bars)

        self.max_line_width = float(max_line_width)
        self.line_height = float(line_height)

        self.min_bars_for_justify = int(min_bars_for_justify)
        self.min_bars_for_smart_justify = int(min_bars_for_smart_justify)


class LayoutEngine:
    """
    LayoutEngine (v2.0.0):
    - berie sekvenciu symbolov (noty, pomlky, taktové čiary, ...)
    - produkuje riadkový layout s rozostupmi a skupinami taktov
    - stabilné spracovanie, bezpečné fallbacky
    """

    def __init__(self, config: LayoutConfig | None = None):
        self.config = config or LayoutConfig()
        Logger.info("LayoutEngine initialized with full layout configuration.")

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def layout(self, symbols: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        if not isinstance(symbols, list) or not symbols:
            Logger.warning("LayoutEngine.layout called with empty or invalid symbol list.")
            return []

        try:
            bars = self._group_into_bars(symbols)
            if not bars:
                return []
            lines = self._break_into_lines(bars)
            if not lines:
                return []
            laid_out = self._apply_spacing(lines)

            Logger.info(f"LayoutEngine produced {len(laid_out)} lines.")
            return laid_out

        except Exception as e:
            Logger.error(f"LayoutEngine.layout error: {e}")
            return []

    # ---------------------------------------------------------
    # 1) Grouping into bars
    # ---------------------------------------------------------
    def _group_into_bars(self, symbols: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        bars: List[List[Dict[str, Any]]] = []
        current_bar: List[Dict[str, Any]] = []

        for sym in symbols:
            if not isinstance(sym, dict):
                continue

            current_bar.append(sym)
            if sym.get("type") == "barline":
                if current_bar:
                    bars.append(current_bar)
                current_bar = []

        if current_bar:
            bars.append(current_bar)

        Logger.info(f"LayoutEngine: grouped into {len(bars)} bars.")
        return bars

    # ---------------------------------------------------------
    # 2) Line breaking
    # ---------------------------------------------------------
    def _break_into_lines(self, bars: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        lines: List[List[Dict[str, Any]]] = []
        current_line: List[Dict[str, Any]] = []
        current_width: float = 0.0

        for bar in bars:
            if not isinstance(bar, list) or not bar:
                continue

            try:
                bar_width = self._estimate_bar_width(bar)
            except Exception:
                bar_width = 0.0

            if current_width + bar_width > self.config.max_line_width and current_line:
                lines.append(current_line)
                current_line = []
                current_width = 0.0

            current_line.extend([s for s in bar if isinstance(s, dict)])
            current_width += bar_width

        if current_line:
            lines.append(current_line)

        Logger.info(f"LayoutEngine: broken into {len(lines)} lines.")
        return lines

    def _estimate_bar_width(self, bar: List[Dict[str, Any]]) -> float:
        width = 0.0
        for sym in bar:
            if not isinstance(sym, dict):
                continue
            try:
                width += self._spacing_for_symbol(sym)
            except Exception:
                width += self.config.min_spacing
        return width

    # ---------------------------------------------------------
    # 3) SMART JUSTIFY 2.0 + CENTER LAST LINE + NO JUSTIFY ON SHORT LINES
    # ---------------------------------------------------------
    def _apply_spacing(self, lines: List[List[Dict[str, Any]]]) -> List[List[Dict[str, Any]]]:
        laid_out_lines: List[List[Dict[str, Any]]] = []
        if not lines:
            return laid_out_lines

        last_line_index = len(lines) - 1
        line_index = 0

        for line in lines:
            if not isinstance(line, list) or not line:
                line_index += 1
                continue

            # Rozdeliť symboly do taktov
            bars: List[List[Dict[str, Any]]] = []
            current_bar: List[Dict[str, Any]] = []

            for sym in line:
                if not isinstance(sym, dict):
                    continue
                current_bar.append(sym)
                if sym.get("type") == "barline":
                    if current_bar:
                        bars.append(current_bar)
                    current_bar = []
            if current_bar:
                bars.append(current_bar)

            if not bars:
                line_index += 1
                continue

            bar_count = len(bars)

            # Šírka každého taktu
            bar_widths: List[float] = []
            for bar in bars:
                try:
                    bar_widths.append(
                        sum(self._spacing_for_symbol(s) for s in bar if isinstance(s, dict))
                    )
                except Exception:
                    bar_widths.append(0.0)

            total_original_width = sum(bar_widths)

            # Rytmická váha každého taktu
            bar_rhythm_weights: List[float] = []
            for bar in bars:
                weight = 0.0
                for s in bar:
                    if not isinstance(s, dict):
                        continue
                    if s.get("type") == "barline":
                        continue
                    dur = s.get("duration", 0.25)
                    try:
                        dur = float(dur)
                    except Exception:
                        dur = 0.25

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
                x_pos = (self.config.max_line_width - total_original_width) / 2.0
                laid_out_line: List[Dict[str, Any]] = []

                for bar_idx, bar in enumerate(bars):
                    for sym in bar:
                        spacing = self._spacing_for_symbol(sym)

                        laid_out_line.append(
                            {
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
                            }
                        )

                        x_pos += spacing

                laid_out_lines.append(laid_out_line)
                line_index += 1
                continue

            # NO JUSTIFY ON SHORT LINES
            if bar_count < self.config.min_bars_for_justify:
                laid_out_line: List[Dict[str, Any]] = []
                x_pos = 0.0
                for bar_idx, bar in enumerate(bars):
                    for sym in bar:
                        spacing = self._spacing_for_symbol(sym)
                        laid_out_line.append(
                            {
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
                            }
                        )
                        x_pos += spacing

                laid_out_lines.append(laid_out_line)
                line_index += 1
                continue

            # JUSTIFY / SMART JUSTIFY 2.0
            remaining = max(self.config.max_line_width - total_original_width, 0.0)

            if bar_count >= self.config.min_bars_for_smart_justify:
                total_weight = sum(bar_rhythm_weights) or 1.0
                bar_extra = [remaining * (rw / total_weight) for rw in bar_rhythm_weights]
                mode = "smart_justify_2_0"
            else:
                total_bar_weight = sum(bar_widths) or 1.0
                bar_extra = [remaining * (bw / total_bar_weight) for bw in bar_widths]
                mode = "justify_width_based"

            laid_out_line: List[Dict[str, Any]] = []
            x_pos = 0.0

            for bar_idx, (bar, extra_width) in enumerate(zip(bars, bar_extra)):
                gaps = max(len(bar) - 1, 1)
                extra_per_symbol = extra_width / gaps if gaps > 0 else 0.0

                for i, sym in enumerate(bar):
                    base_spacing = self._spacing_for_symbol(sym)

                    if i < len(bar) - 1:
                        spacing = base_spacing + extra_per_symbol
                        extra = extra_per_symbol
                    else:
                        spacing = base_spacing
                        extra = 0.0

                    laid_out_line.append(
                        {
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
                        }
                    )

                    x_pos += spacing

            laid_out_lines.append(laid_out_line)
            line_index += 1

        return laid_out_lines

    def _spacing_for_symbol(self, symbol: Dict[str, Any]) -> float:
        if not isinstance(symbol, dict):
            return self.config.min_spacing

        sym_type = symbol.get("type")
        duration = symbol.get("duration", 0.25)

        if sym_type == "barline":
            return self.config.barline_spacing

        try:
            dur = float(duration)
        except Exception:
            dur = 0.25

        base = dur * 8.0
        return max(self.config.min_spacing, min(self.config.max_spacing, base))


# -------------------------------------------------------------------------
# PixelLayoutEngine v2.0.0 – grafický layout pre renderer (x/y pozície)
# -------------------------------------------------------------------------
class PixelLayoutEngine:
    def __init__(
        self,
        note_spacing: float = 40.0,
        measure_width: float = 480.0,
        staff_top: float = 80.0,
        staff_spacing: float = 140.0,
    ):
        self.note_spacing = float(note_spacing)
        self.measure_width = float(measure_width)
        self.staff_top = float(staff_top)
        self.staff_spacing = float(staff_spacing)

        self.track_offsets: Dict[str, float] = {
            "melody": 0.0,
            "bass": staff_spacing,
            "drums": staff_spacing * 2,
            "chords": staff_spacing * 3,
        }

        self.drum_y_map: Dict[int, float] = {
            36: +20.0,
            38: 0.0,
            42: -20.0,
            46: -20.0,
            49: -40.0,
            51: -40.0,
        }

        self.reference_pitch: int = 60
        self.pitch_step: float = 3.0

    # ---------------------------------------------------------
    # TIMELINE LAYOUT
    # ---------------------------------------------------------
    def layout_timeline(self, timeline: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if not isinstance(timeline, list):
            return []

        try:
            annotated = annotate_drum_timeline(timeline)
        except Exception:
            annotated = timeline

        result: List[Dict[str, Any]] = []
        for note in annotated:
            if not isinstance(note, dict):
                continue
            try:
                result.append(self.layout_note(note))
            except Exception:
                continue
        return result

    def layout_single(self, note: Dict[str, Any]) -> Dict[str, Any]:
        return self.layout_note(note)

    def layout_note(self, note: Dict[str, Any]) -> Dict[str, Any]:
        return {
            **note,
            "x": self._compute_x(note),
            "y": self._compute_y(note),
        }

    def _compute_x(self, note: Dict[str, Any]) -> float:
        try:
            start = float(note.get("start", 0.0))
        except Exception:
            start = 0.0
        return start * self.note_spacing

    def _compute_y(self, note: Dict[str, Any]) -> float:
        pitch = note.get("pitch", self.reference_pitch)
        track_type = note.get("track_type", "melody")

        base_y = self._get_track_base_y(track_type)

        if track_type == "drums":
            try:
                p = int(pitch)
            except Exception:
                p = 38
            return base_y + self.drum_y_map.get(p, 0.0)

        try:
            p = int(pitch)
        except Exception:
            p = self.reference_pitch

        dy = (self.reference_pitch - p) * self.pitch_step
        return base_y + dy

    def _get_track_base_y(self, track_type: str) -> float:
        try:
            offset = self.track_offsets.get(str(track_type), 0.0)
        except Exception:
            offset = 0.0
        return self.staff_top + offset
