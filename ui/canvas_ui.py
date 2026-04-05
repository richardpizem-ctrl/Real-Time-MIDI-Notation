import tkinter as tk


class CanvasUI:
    def __init__(self, parent):
        # Main canvas
        self.canvas = tk.Canvas(parent, bg="white", width=1100, height=700)
        self.canvas.pack(fill="both", expand=True)

        # Viewport transform
        self.offset_x = 0
        self.offset_y = 0
        self.zoom = 1.0

        # Playhead
        self.playhead_x = 100
        self.playhead_color = "#ff4444"
        self.playhead_width = 2

        # Timeline
        self.timeline_height = 30
        self.timeline_bg = "#f0f0f0"
        self.timeline_line_color = "#888"

        # Dragging
        self.dragging = False
        self.last_drag_x = 0
        self.last_drag_y = 0

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
        """UIManager volá túto funkciu pri update času."""
        self.playhead_x = int((time_ms / 1000.0) * pixels_per_second)
        self._center_playhead_if_needed()

    # ---------------------------------------------------------
    # INTERNAL: REDRAW LOOP
    # ---------------------------------------------------------
    def _schedule_redraw(self):
        self._draw()
        self.canvas.after(16, self._schedule_redraw)  # ~60 FPS

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def _draw(self):
        self.canvas.delete("all")

        # Timeline background
        self.canvas.create_rectangle(
            0, 0, self.canvas.winfo_width(), self.timeline_height,
            fill=self.timeline_bg, outline=""
        )

        # Timeline ticks
        width = self.canvas.winfo_width()
        for x in range(0, width, 100):
            self.canvas.create_line(
                x, 0, x, self.timeline_height,
                fill=self.timeline_line_color
            )
            self.canvas.create_text(
                x + 2, 15,
                text=f"{x//100}s",
                anchor="w",
                fill="#555"
            )

        # Playhead
        self.canvas.create_line(
            self.playhead_x, 0,
            self.playhead_x, self.canvas.winfo_height(),
            fill=self.playhead_color,
            width=self.playhead_width
        )

        # TODO: future drawing of notes, grid, selection, etc.

    # ---------------------------------------------------------
    # MOUSE EVENTS
    # ---------------------------------------------------------
    def _on_mouse_down(self, event):
        if event.y <= self.timeline_height:
            # Click into timeline → move playhead
            self.playhead_x = event.x
        else:
            # Start dragging
            self.dragging = True
            self.last_drag_x = event.x
            self.last_drag_y = event.y

    def _on_mouse_up(self, event):
        self.dragging = False

    def _on_mouse_drag(self, event):
        if not self.dragging:
            return

        dx = event.x - self.last_drag_x
        dy = event.y - self.last_drag_y

        self.offset_x += dx
        self.offset_y += dy

        self.last_drag_x = event.x
        self.last_drag_y = event.y

    # ---------------------------------------------------------
    # ZOOM
    # ---------------------------------------------------------
    def _on_mouse_wheel(self, event):
        # Ctrl + wheel → zoom
        if event.state & 0x0004:  # Ctrl key
            if event.delta > 0:
                self.zoom *= 1.1
            else:
                self.zoom /= 1.1
            self.zoom = max(0.2, min(4.0, self.zoom))
        else:
            # Normal wheel → vertical scroll
            self.offset_y += -event.delta * 0.1

    # ---------------------------------------------------------
    # PLAYHEAD CENTERING
    # ---------------------------------------------------------
    def _center_playhead_if_needed(self):
        """Ak playhead utečie mimo obrazovky, posunieme viewport."""
        width = self.canvas.winfo_width()
        margin = 200

        if self.playhead_x > width - margin:
            self.offset_x -= (self.playhead_x - (width - margin))

        if self.playhead_x < margin:
            self.offset_x += (margin - self.playhead_x)
