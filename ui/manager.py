# ---------------------------------------------------------
# DRAW NOTE (v4.3.0)
# Ultra‑optimalizovaná verzia pre real‑time rendering
# ---------------------------------------------------------
def _draw_note(self, note: dict, preview: bool = False) -> None:
    """
    Kreslí jednu MIDI notu (v4.3.0 optimalizácia).
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

    # --- COLOR (predpočítané velocity farby) ---
    fill = self._velocity_to_color(velocity)

    # Preview má jemnejší outline
    outline = "#555555" if preview else "#222222"

    # --- MAIN BODY ---
    self.canvas.create_rectangle(
        x0, y0, x1, y1,
        fill=fill,
        outline=outline,
        width=1
    )

    # Preview = bez highlightov
    if preview:
        return

    # --- TOP HIGHLIGHT (3 px) ---
    self.canvas.create_rectangle(
        x0, y0, x1, y0 + 3,
        fill="#ffffff",
        outline=""
    )

    # --- BOTTOM SHADOW (3 px) ---
    self.canvas.create_rectangle(
        x0, y1 - 3, x1, y1,
        fill="#000000",
        outline=""
    )
