# =========================================================
# CanvasUI v2.0.0
# Stabilná real‑time piano‑roll vizualizácia (Tkinter)
# =========================================================

import tkinter as tk
import time


class CanvasUI:
    GRID_STEP_TIME = 100
    ROW_HEIGHT = 16
    MIN_ZOOM = 0.25
    MAX_ZOOM = 4.0

    def __init__(self, parent: tk.Misc):
        # Main canvas
        self.canvas = tk.Canvas(parent, bg="white", width=1100, height=700)
        self.canvas.pack(fill="both", expand=True)

        # Viewport transform
        self.offset_x = 0.0
        self.offset_y = 40.0
        self.zoom = 1.0

        # Playhead
        self.playhead_time = 1000.0
        self.playhead_color = "#ff4444"
        self.playhead_width = 2

        # Timeline
        self.timeline_height = 30
        self.timeline_bg = "#f0f0f0"
        self.timeline_line_color = "#888"

        # Notes
        self.notes: list[dict] = []
        self.current_note: dict | None = None

        # Velocity editing
        self.velocity_min = 1
        self.velocity_max = 127
        self._velocity_target_note: dict | None = None

        # Tools
        self.tool = "draw"
        self.snap = True
        self.snap_step = self.GRID_STEP_TIME

        # Quantization
        self.quantize_division = 1.0
        self.swing_amount = 0.0

        # Dragging viewport
        self.dragging_view = False
        self.last_drag_x = 0
        self.last_drag_y = 0

        # Selection box
        self.selecting = False
        self.selection_start: tuple[float, float] | None = None
        self.selection_end: tuple[float, float] | None = None

        # Color modes
        self.color_mode = "heatmap"

        # Bind events
        self._bind_events()

        # Redraw loop
        self._schedule_redraw()

    # ---------------------------------------------------------
    # EVENT BINDING
    # ---------------------------------------------------------
    def _bind_events(self) -> None:
        c = self.canvas

        # Left mouse
        c.bind("<ButtonPress-1>", self._on_mouse_down)
        c.bind("<ButtonRelease-1>", self._on_mouse_up)
        c.bind("<B1-Motion>", self._on_mouse_drag)

        # Mouse wheel (Windows / Linux / macOS)
        c.bind("<MouseWheel>", self._on_mouse_wheel)
        c.bind("<Button-4>", self._on_mouse_wheel)
        c.bind("<Button-5>", self._on_mouse_wheel)

        # Right mouse → velocity edit
        c.bind("<ButtonPress-3>", self._on_right_mouse_down)
        c.bind("<B3-Motion>", self._on_right_mouse_drag)
        c.bind("<ButtonRelease-3>", self._on_right_mouse_up)

    # ---------------------------------------------------------
    # PUBLIC API (UIManager-safe)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str) -> None:
        return

    def update_visibility(self, track_index: int, visible: bool) -> None:
        return

    def set_active_track(self, track_index: int) -> None:
        return

    def get_canvas(self) -> tk.Canvas:
        return self.canvas

    def set_playhead_time(self, time_ms: float, pixels_per_second: float = 100.0) -> None:
        """Nastaví internú playhead pozíciu na základe času v ms a mierky px/s."""
        try:
            self.playhead_time = (float(time_ms) / 1000.0) * float(pixels_per_second)
        except Exception:
            return
        self._center_playhead_if_needed()

    def set_tool(self, tool_name: str) -> None:
        if tool_name in ("draw", "select", "erase"):
            self.tool = tool_name

    def set_color_mode(self, mode: str) -> None:
        if mode in ("classic", "heatmap", "glow"):
            self.color_mode = mode

    # ---------------------------------------------------------
    # QUANTIZATION
    # ---------------------------------------------------------
    def set_quantization(self, division: float) -> None:
        try:
            d = float(division)
        except Exception:
            return
        self.quantize_division = max(0.03125, min(4.0, d))
        self.snap_step = self.GRID_STEP_TIME * self.quantize_division

    def set_swing(self, amount: float) -> None:
        try:
            a = float(amount)
        except Exception:
            return
        self.swing_amount = max(0.0, min(0.5, a))

    # ---------------------------------------------------------
    # REDRAW LOOP
    # ---------------------------------------------------------
    def _schedule_redraw(self) -> None:
        self._draw()
        self.canvas.after(16, self._schedule_redraw)

    # ---------------------------------------------------------
    # COORD TRANSFORMS
    # ---------------------------------------------------------
    def _time_to_screen_x(self, t: float) -> float:
        return t * self.zoom + self.offset_x

    def _screen_x_to_time(self, x: float) -> float:
        return (x - self.offset_x) / max(self.zoom, 1e-6)

    def _row_to_screen_y(self, row: int) -> float:
        return self.timeline_height + row * self.ROW_HEIGHT + self.offset_y

    def _screen_y_to_row(self, y: float) -> int:
        return int((y - self.timeline_height - self.offset_y) / self.ROW_HEIGHT)

    def _snap_time(self, t: float) -> float:
        if not self.snap:
            return t

        step = self.snap_step
        base = round(t / step) * step

        if self.swing_amount == 0.0:
            return base

        index = round(t / step)
        if index % 2 == 1:
            base += step * self.swing_amount

        return base

    # ---------------------------------------------------------
    # COLOR HELPERS
    # ---------------------------------------------------------
    def _hex_to_rgb(self, h: str) -> tuple[int, int, int]:
        h = h.lstrip("#")
        if len(h) != 6:
            return 0, 0, 0
        try:
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        except Exception:
            return 0, 0, 0

    def _rgb_to_hex(self, r: int, g: int, b: int) -> str:
        return f"#{r:02x}{g:02x}{b:02x}"

    def _lerp(self, a: int, b: int, t: float) -> int:
        return int(a + (b - a) * t)

    def _mix_colors(self, c1: str, c2: str, t: float) -> str:
        r1, g1, b1 = self._hex_to_rgb(c1)
        r2, g2, b2 = self._hex_to_rgb(c2)
        r = self._lerp(r1, r2, t)
        g = self._lerp(g1, g2, t)
        b = self._lerp(b1, b2, t)
        return self._rgb_to_hex(r, g, b)

    def _velocity_to_color(self, velocity: int) -> str:
        v = max(self.velocity_min, min(self.velocity_max, int(velocity)))
        t = v / float(self.velocity_max)

        if self.color_mode == "classic":
            return "#66aaff"

        blue = (0x4D, 0xA6, 0xFF)
        green = (0x33, 0xCC, 0x33)
        red = (0xFF, 0x44, 0x44)

        if t <= 0.5:
            lt = t / 0.5
            r = self._lerp(blue[0], green[0], lt)
            g = self._lerp(blue[1], green[1], lt)
            b = self._lerp(blue[2], green[2], lt)
        else:
            lt = (t - 0.5) / 0.5
            r = self._lerp(green[0], red[0], lt)
            g = self._lerp(green[1], red[1], lt)
            b = self._lerp(green[2], red[2], lt)

        base = self._rgb_to_hex(r, g, b)

        if self.color_mode == "glow":
            base = self._mix_colors(base, "#ffffff", 0.35)

        return base

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def _draw(self) -> None:
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Timeline
        self.canvas.create_rectangle(
            0, 0, width, self.timeline_height,
            fill=self.timeline_bg, outline=""
        )

        max_time = self._screen_x_to_time(width + 200)
        min_time = self._screen_x_to_time(-200)

        # Common start for grid/ticks
        t_start = (min_time // self.GRID_STEP_TIME) * self.GRID_STEP_TIME

        # Timeline ticks
        t = t_start
        while t < max_time:
            x = self._time_to_screen_x(t)
            if 0 <= x <= width:
                self.canvas.create_line(
                    x, 0, x, self.timeline_height,
                    fill=self.timeline_line_color
                )
                self.canvas.create_text(
                    x + 2, self.timeline_height // 2,
                    text=f"{int(t / self.GRID_STEP_TIME)}",
                    anchor="w",
                    fill="#555"
                )
            t += self.GRID_STEP_TIME

        # Grid rows
        max_rows = int((height - self.timeline_height) / self.ROW_HEIGHT) + 4
        for r in range(-2, max_rows):
            y = self._row_to_screen_y(r)
            if 0 <= y <= height:
                color = "#f7f7f7" if r % 2 == 0 else "#f0f0f0"
                self.canvas.create_rectangle(
                    0, y, width, y + self.ROW_HEIGHT,
                    fill=color, outline=""
                )

        # Vertical grid lines
        t = t_start
        while t < max_time:
            x = self._time_to_screen_x(t)
            if 0 <= x <= width:
                self.canvas.create_line(
                    x, self.timeline_height, x, height,
                    fill="#dddddd"
                )
            t += self.GRID_STEP_TIME

        # Notes
        for note in self.notes:
            self._draw_note(note)

        if self.current_note is not None:
            self._draw_note(self.current_note, preview=True)

        # Selection box
        if self.selecting and self.selection_start and self.selection_end:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline="#3399ff",
                dash=(3, 3)
            )

        # Playhead
        px = self._time_to_screen_x(self.playhead_time)
        self.canvas.create_line(
            px, 0, px, height,
            fill=self.playhead_color,
            width=self.playhead_width
        )

        # Legend
        self._draw_legend(width, height)

    # ---------------------------------------------------------
    # LEGEND
    # ---------------------------------------------------------
    def _draw_legend(self, width: int, height: int) -> None:
        legend_height = 22
        y0 = height - legend_height
        y1 = height

        self.canvas.create_rectangle(
            0, y0, width, y1,
            fill="#f8f8f8",
            outline="#dddddd"
        )

        x0 = 10
        x1 = 210
        steps = 50

        for i in range(steps):
            t = i / (steps - 1)
            v = int(t * self.velocity_max)
            color = self._velocity_to_color(v)
            sx0 = x0 + (x1 - x0) * t
            sx1 = x0 + (x1 - x0) * ((i + 1) / (steps - 1))
            self.canvas.create_rectangle(
                sx0, y0 + 4, sx1, y1 - 4,
                fill=color,
                outline=color
            )

        self.canvas.create_text(
            x1 + 10, (y0 + y1) / 2,
            text="Soft → Strong (velocity)",
            anchor="w",
            fill="#444",
            font=("TkDefaultFont", 8)
        )

        self.canvas.create_text(
            width - 10, (y0 + y1) / 2,
            text=f"Color mode: {self.color_mode}",
            anchor="e",
            fill="#666",
            font=("TkDefaultFont", 8)
        )

    # ---------------------------------------------------------
    # PLACEHOLDER HANDLERS (v2.0.0 – bezpečné no-op)
    # ---------------------------------------------------------
    def _on_mouse_down(self, event) -> None:
        pass

    def _on_mouse_up(self, event) -> None:
        pass

    def _on_mouse_drag(self, event) -> None:
        pass

    def _on_mouse_wheel(self, event) -> None:
        pass

    def _on_right_mouse_down(self, event) -> None:
        pass

    def _on_right_mouse_drag(self, event) -> None:
        pass

    def _on_right_mouse_up(self, event) -> None:
        pass

    def _center_playhead_if_needed(self) -> None:
        pass

    def _draw_note(self, note: dict, preview: bool = False) -> None:
        pass
