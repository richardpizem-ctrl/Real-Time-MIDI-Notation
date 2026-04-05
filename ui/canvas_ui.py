import tkinter as tk


class CanvasUI:
    GRID_STEP_TIME = 100        # logical time units between grid lines
    ROW_HEIGHT = 16             # height of one pitch row
    MIN_ZOOM = 0.25
    MAX_ZOOM = 4.0

    def __init__(self, parent):
        # Main canvas
        self.canvas = tk.Canvas(parent, bg="white", width=1100, height=700)
        self.canvas.pack(fill="both", expand=True)

        # Viewport transform
        self.offset_x = 0
        self.offset_y = 40  # nech je trochu miesta nad prvým riadkom
        self.zoom = 1.0

        # Playhead (logical x, in same units as notes/grid)
        self.playhead_time = 1000  # ms-based default, but treated as logical units
        self.playhead_color = "#ff4444"
        self.playhead_width = 2

        # Timeline
        self.timeline_height = 30
        self.timeline_bg = "#f0f0f0"
        self.timeline_line_color = "#888"

        # Notes (hybrid: piano-roll rect + notation symbol)
        # each note: {"x": float, "width": float, "row": int, "selected": bool}
        self.notes = []
        self.current_note = None

        # Tools
        self.tool = "draw"  # "draw", "select", "erase"
        self.snap = True
        self.snap_step = self.GRID_STEP_TIME  # snap to grid

        # Dragging viewport
        self.dragging_view = False
        self.last_drag_x = 0
        self.last_drag_y = 0

        # Selection box
        self.selecting = False
        self.selection_start = None
        self.selection_end = None

        # Bind events
        self.canvas.bind("<ButtonPress-1>", self._on_mouse_down)
        self.canvas.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.canvas.bind("<B1-Motion>", self._on_mouse_drag)
        self.canvas.bind("<MouseWheel>", self._on_mouse_wheel)
        self.canvas.bind("<Button-4>", self._on_mouse_wheel)  # Linux
        self.canvas.bind("<Button-5>", self._on_mouse_wheel)  # Linux

        # Redraw loop
        self._schedule_redraw()

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------
    def get_canvas(self):
        return self.canvas

    def set_playhead_time(self, time_ms, pixels_per_second=100):
        """
        UIManager volá túto funkciu pri update času.
        time_ms je len logická hodnota – tu ju prepočítame na "time units".
        """
        self.playhead_time = (time_ms / 1000.0) * pixels_per_second
        self._center_playhead_if_needed()

    def set_tool(self, tool_name):
        """
        Nastavenie nástroja z vonku: "draw", "select", "erase".
        """
        if tool_name in ("draw", "select", "erase"):
            self.tool = tool_name

    # ---------------------------------------------------------
    # INTERNAL: REDRAW LOOP
    # ---------------------------------------------------------
    def _schedule_redraw(self):
        self._draw()
        self.canvas.after(16, self._schedule_redraw)  # ~60 FPS

    # ---------------------------------------------------------
    # COORD TRANSFORMS
    # ---------------------------------------------------------
    def _time_to_screen_x(self, t):
        return t * self.zoom + self.offset_x

    def _screen_x_to_time(self, x):
        return (x - self.offset_x) / max(self.zoom, 1e-6)

    def _row_to_screen_y(self, row):
        return self.timeline_height + row * self.ROW_HEIGHT + self.offset_y

    def _screen_y_to_row(self, y):
        return int((y - self.timeline_height - self.offset_y) / self.ROW_HEIGHT)

    def _snap_time(self, t):
        if not self.snap:
            return t
        step = self.snap_step
        return round(t / step) * step

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def _draw(self):
        self.canvas.delete("all")

        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()

        # Timeline background
        self.canvas.create_rectangle(
            0, 0, width, self.timeline_height,
            fill=self.timeline_bg, outline=""
        )

        # Timeline ticks (based on logical time)
        max_time = self._screen_x_to_time(width + 200)
        min_time = self._screen_x_to_time(-200)
        t = (min_time // self.GRID_STEP_TIME) * self.GRID_STEP_TIME
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

        # Piano-roll grid (horizontal rows + vertical lines)
        # Horizontal rows
        max_rows = int((height - self.timeline_height) / self.ROW_HEIGHT) + 4
        for r in range(-2, max_rows):
            y = self._row_to_screen_y(r)
            if 0 <= y <= height:
                color = "#f7f7f7" if r % 2 == 0 else "#f0f0f0"
                self.canvas.create_rectangle(
                    0, y, width, y + self.ROW_HEIGHT,
                    fill=color, outline=""
                )

        # Vertical grid lines (extend through editor area)
        t = (min_time // self.GRID_STEP_TIME) * self.GRID_STEP_TIME
        while t < max_time:
            x = self._time_to_screen_x(t)
            if 0 <= x <= width:
                self.canvas.create_line(
                    x, self.timeline_height,
                    x, height,
                    fill="#dddddd"
                )
            t += self.GRID_STEP_TIME

        # Notes (hybrid: rect + notation symbol)
        for note in self.notes:
            self._draw_note(note)

        # Current drawing note
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
            px, 0,
            px, height,
            fill=self.playhead_color,
            width=self.playhead_width
        )

    def _draw_note(self, note, preview=False):
        x = self._time_to_screen_x(note["x"])
        w = note["width"] * self.zoom
        y = self._row_to_screen_y(note["row"])
        h = self.ROW_HEIGHT - 2

        fill = "#66aaff" if not note.get("selected", False) else "#ffcc66"
        outline = "#225588" if not preview else "#888888"

        self.canvas.create_rectangle(
            x, y, x + w, y + h,
            fill=fill,
            outline=outline,
            width=1
        )

        # Hybrid overlay – malý notový symbol
        self.canvas.create_text(
            x + 4, y + h / 2,
            text="♩",
            anchor="w",
            fill="#102030"
        )

    # ---------------------------------------------------------
    # MOUSE EVENTS
    # ---------------------------------------------------------
    def _on_mouse_down(self, event):
        # Timeline click → move playhead
        if event.y <= self.timeline_height:
            self.playhead_time = self._screen_x_to_time(event.x)
            self._center_playhead_if_needed()
            return

        # Tools
        if self.tool == "draw":
            self._start_draw_note(event)
        elif self.tool == "erase":
            self._erase_at(event)
        elif self.tool == "select":
            self._start_selection(event)
        else:
            # fallback: drag viewport
            self.dragging_view = True
            self.last_drag_x = event.x
            self.last_drag_y = event.y

    def _on_mouse_up(self, event):
        if self.tool == "draw":
            if self.current_note is not None:
                if self.current_note["width"] > 5:
                    self.notes.append(self.current_note)
                self.current_note = None

        if self.tool == "select" and self.selecting:
            self._finalize_selection()
            self.selecting = False
            self.selection_start = None
            self.selection_end = None

        self.dragging_view = False

    def _on_mouse_drag(self, event):
        if self.tool == "draw":
            self._update_draw_note(event)
            return

        if self.tool == "select" and self.selecting:
            self.selection_end = (event.x, event.y)
            return

        # viewport drag (middle of editor)
        if not self.dragging_view:
            self.dragging_view = True
            self.last_drag_x = event.x
            self.last_drag_y = event.y
            return

        dx = event.x - self.last_drag_x
        dy = event.y - self.last_drag_y

        self.offset_x += dx
        self.offset_y += dy

        self.last_drag_x = event.x
        self.last_drag_y = event.y

    # ---------------------------------------------------------
    # DRAW TOOL
    # ---------------------------------------------------------
    def _start_draw_note(self, event):
        if event.y <= self.timeline_height:
            return

        t = self._screen_x_to_time(event.x)
        t = self._snap_time(t)
        row = self._screen_y_to_row(event.y)

        self.current_note = {
            "x": t,
            "width": self.snap_step,
            "row": row,
            "selected": False,
        }

    def _update_draw_note(self, event):
        if self.current_note is None:
            return

        t_end = self._screen_x_to_time(event.x)
        t_end = self._snap_time(t_end)
        width = max(self.snap_step, t_end - self.current_note["x"])
        self.current_note["width"] = width

    # ---------------------------------------------------------
    # ERASE TOOL
    # ---------------------------------------------------------
    def _erase_at(self, event):
        t = self._screen_x_to_time(event.x)
        row = self._screen_y_to_row(event.y)

        hit = None
        for note in self.notes:
            if note["row"] != row:
                continue
            if note["x"] <= t <= note["x"] + note["width"]:
                hit = note
                break

        if hit is not None:
            self.notes.remove(hit)

    # ---------------------------------------------------------
    # SELECTION TOOL
    # ---------------------------------------------------------
    def _start_selection(self, event):
        self.selecting = True
        self.selection_start = (event.x, event.y)
        self.selection_end = (event.x, event.y)
        # reset selection
        for n in self.notes:
            n["selected"] = False

    def _finalize_selection(self):
        if not self.selection_start or not self.selection_end:
            return

        x1, y1 = self.selection_start
        x2, y2 = self.selection_end
        sx1, sx2 = sorted([x1, x2])
        sy1, sy2 = sorted([y1, y2])

        for note in self.notes:
            x = self._time_to_screen_x(note["x"])
            w = note["width"] * self.zoom
            y = self._row_to_screen_y(note["row"])
            h = self.ROW_HEIGHT - 2

            if (x + w) >= sx1 and x <= sx2 and (y + h) >= sy1 and y <= sy2:
                note["selected"] = True

    # ---------------------------------------------------------
    # ZOOM
    # ---------------------------------------------------------
    def _on_mouse_wheel(self, event):
        # Ctrl + wheel → zoom (x-axis)
        ctrl_pressed = (event.state & 0x0004) != 0

        if ctrl_pressed:
            old_zoom = self.zoom
            if getattr(event, "delta", 0) > 0 or getattr(event, "num", None) == 4:
                self.zoom *= 1.1
            else:
                self.zoom /= 1.1

            self.zoom = max(self.MIN_ZOOM, min(self.MAX_ZOOM, self.zoom))

            # zoom around cursor
            if self.zoom != old_zoom:
                mouse_time = self._screen_x_to_time(event.x)
                new_offset_x = event.x - mouse_time * self.zoom
                self.offset_x = new_offset_x
        else:
            # Normal wheel → vertical scroll
            delta = getattr(event, "delta", 0)
            if delta == 0:
                # Linux Button-4/5
                if getattr(event, "num", None) == 4:
                    delta = 120
                elif getattr(event, "num", None) == 5:
                    delta = -120
            self.offset_y += -delta * 0.1

    # ---------------------------------------------------------
    # PLAYHEAD CENTERING
    # ---------------------------------------------------------
    def _center_playhead_if_needed(self):
        """Ak playhead utečie mimo obrazovky, posunieme viewport."""
        width = self.canvas.winfo_width()
        margin = 200

        px = self._time_to_screen_x(self.playhead_time)

        if px > width - margin:
            self.offset_x -= (px - (width - margin))

        if px < margin:
            self.offset_x += (margin - px)
