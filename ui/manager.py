    # ---------------------------------------------------------
    # DRAW NOTE (v4.0.0)
    # ---------------------------------------------------------
    def _draw_note(self, note: dict, preview: bool = False) -> None:
        """
        Kreslí jednu MIDI notu.
        Očakávaný formát:
            {
                "start": time_ms,
                "end": time_ms,
                "pitch": int,
                "velocity": int
            }
        """
        # --- SAFE PARSING ---
        try:
            start = float(note.get("start", 0.0))
            end = float(note.get("end", start + 100.0))
            pitch = int(note.get("pitch", 60))
            velocity = int(note.get("velocity", 80))
        except Exception:
            return

        # --- TIME → X ---
        x0 = self._time_to_screen_x(start)
        x1 = self._time_to_screen_x(end)

        if x1 < x0:
            x0, x1 = x1, x0

        # --- PITCH → Y ---
        y0 = self._row_to_screen_y(pitch)
        y1 = y0 + self.ROW_HEIGHT - 2

        # --- COLOR ---
        base_color = self._velocity_to_color(velocity)

        if preview:
            fill = base_color
            outline = "#555555"
        else:
            fill = base_color
            outline = "#222222"

        # --- MAIN BODY ---
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=fill,
            outline=outline,
            width=1
        )

        if preview:
            return  # preview = bez highlightov

        # --- TOP HIGHLIGHT ---
        self.canvas.create_rectangle(
            x0, y0, x1, y0 + 3,
            fill="#ffffff",
            outline=""
        )

        # --- BOTTOM SHADOW ---
        self.canvas.create_rectangle(
            x0, y1 - 3, x1, y1,
            fill="#000000",
            outline=""
        )
