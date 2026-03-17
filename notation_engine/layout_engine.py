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
        line_break_on_bars=True
    ):
        self.max_symbols_per_line = max_symbols_per_line
        self.min_spacing = min_spacing
        self.max_spacing = max_spacing
        self.barline_spacing = barline_spacing
        self.line_break_on_bars = line_break_on_bars


class LayoutEngine:
    """
    Takes a sequence of notation symbols (notes, rests, barlines, etc.)
    and produces a line-based layout with spacing and bar grouping.
    """

    def __init__(self, config=None):
        self.config = config or LayoutConfig()
        Logger.info("LayoutEngine initialized with full layout configuration.")

    def layout(self, symbols):
        """
        Main entry point.
        Input: list of symbol dicts, e.g.:
            {
                "type": "note" | "rest" | "barline",
                "duration": 0.25,  # quarter, eighth, etc.
                "pitch": "C4",     # optional
                ...
            }
        Output: list of lines, each line is list of layout items:
            {
                "symbol": <original symbol>,
                "x": <position index>,
                "line": <line index>,
                "spacing": <spacing units>
            }
        """
        if not symbols:
            Logger.warning("LayoutEngine.layout called with empty symbol list.")
            return []

        try:
            # 1) Rozdelenie na takty (bars)
            bars = self._group_into_bars(symbols)

            # 2) Rozdelenie na riadky
            lines = self._break_into_lines(bars)

            # 3) Výpočet spacingu v rámci riadkov
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
        """
        Group symbols into bars based on 'barline' type.
        Returns list of bars, each bar is list of symbols.
        """
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
    # 2) Line breaking
    # ------------------------

    def _break_into_lines(self, bars):
        """
        Break bars into lines based on config.max_symbols_per_line
        and optional line_break_on_bars.
        Returns list of lines, each line is list of symbols.
        """
        lines = []
        current_line = []
        symbol_count = 0

        for bar in bars:
            bar_len = len(bar)

            # If adding this bar would exceed max symbols per line → new line
            if symbol_count + bar_len > self.config.max_symbols_per_line and current_line:
                lines.append(current_line)
                current_line = []
                symbol_count = 0

            current_line.extend(bar)
            symbol_count += bar_len

        if current_line:
            lines.append(current_line)

        Logger.info(f"LayoutEngine: broken into {len(lines)} lines.")
        return lines

    # ------------------------
    # 3) Spacing within lines
    # ------------------------

    def _apply_spacing(self, lines):
        """
        Apply spacing based on duration and barlines.
        Returns list of lines, each line is list of layout items.
        """
        laid_out_lines = []
        line_index = 0

        for line in lines:
            x_pos = 0
            laid_out_line = []

            for sym in line:
                spacing = self._spacing_for_symbol(sym)

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
        """
        Determine spacing for a symbol based on its type and duration.
        """
        sym_type = symbol.get("type")
        duration = symbol.get("duration", 0.25)  # default quarter

        # Barline – extra spacing
        if sym_type == "barline":
            return self.config.barline_spacing

        # Notes/rests – duration-based spacing
        # Longer duration → more spacing, clamped between min and max
        base = duration * 8  # scale factor
        spacing = max(self.config.min_spacing, min(self.config.max_spacing, base))

        return spacing

