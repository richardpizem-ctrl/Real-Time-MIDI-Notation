    # ---------------------------------------------------------
    # DRAW NOTE (v2.0.0)
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

        try:
            start = float(note.get("start", 0))
            end = float(note.get("end", start + 100))
            pitch = int(note.get("pitch", 60))
            velocity = int(note.get("velocity", 80))
        except Exception:
            return

        # Čas → X
        x0 = self._time_to_screen_x(start)
        x1 = self._time_to_screen_x(end)

        # Pitch → Y
        row = pitch
        y0 = self._row_to_screen_y(row)
        y1 = y0 + self.ROW_HEIGHT - 2

        # Farba podľa velocity
        color = self._velocity_to_color(velocity)

        # Preview = polopriesvitná nota
        if preview:
            fill = color
            outline = "#444444"
            alpha = 0.45
        else:
            fill = color
            outline = "#222222"
            alpha = 1.0

        # Tkinter nemá alpha → simulujeme cez dve vrstvy
        # vrstva 1: základný obdĺžnik
        self.canvas.create_rectangle(
            x0, y0, x1, y1,
            fill=fill,
            outline=outline,
            width=1
        )

        # vrstva 2: jemný highlight (horný pás)
        if not preview:
            self.canvas.create_rectangle(
                x0, y0, x1, y0 + 3,
                fill="#ffffff",
                outline="",
            )

        # vrstva 3: jemný tieň (spodný pás)
        if not preview:
            self.canvas.create_rectangle(
                x0, y1 - 3, x1, y1,
                fill="#000000",
                outline="",
            )
