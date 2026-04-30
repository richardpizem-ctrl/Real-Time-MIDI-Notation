import pygame
import time
from typing import Dict, List, Tuple, Any


class StaffUI:
    STAFF_LINE_COLOR = (220, 220, 220)
    NOTE_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 80, 80)

    STAFF_TOP = 40
    STAFF_SPACING = 12
    STAFF_LINES = 5

    NOTE_RADIUS = 7
    NOTE_OUTLINE = (30, 30, 30)

    def __init__(self, width: int = 1400, height: int = 200):
        self.width = int(width)
        self.height = int(height)

        # note_id -> {x, y, color, highlight}
        self.notes: Dict[str, Dict[str, Any]] = {}
        self.note_order: List[str] = []  # stabilné poradie nôt

        # scrolling
        self.scroll_x = 0
        self.note_spacing = 22
        self.scroll_speed = 2

    # ---------------------------------------------------------
    # PUBLIC API (pre UIManager – bezpečné no-op metódy)
    # ---------------------------------------------------------
    def update_color(self, track_index: int, color_hex: str):
        return

    def update_visibility(self, track_index: int, visible: bool):
        return

    def set_active_track(self, track_index: int):
        return

    # ---------------------------------------------------------
    # NOTE MANAGEMENT
    # ---------------------------------------------------------
    def add_note(self, event: Dict[str, Any]):
        """
        event:
            track_id
            note (MIDI)
            time
            track_color (optional)
        """
        track = event.get("track_id", 0)
        midi = event.get("note")
        t = event.get("time", time.time())

        if midi is None:
            return

        try:
            midi_int = int(midi)
        except Exception:
            return

        # unikátne ID
        note_id = f"{track}_{midi_int}_{int(t * 1000)}_{len(self.note_order)}"

        if note_id in self.notes:
            return

        self.note_order.append(note_id)

        # X pozícia podľa poradia
        x = len(self.note_order) * self.note_spacing + 100

        # Y pozícia podľa MIDI
        y = self._midi_to_staff_y(midi_int)
        y = max(0, min(self.height - 10, y))

        # farba
        color = event.get("track_color", self.NOTE_COLOR)
        if (
            not isinstance(color, (tuple, list))
            or len(color) != 3
        ):
            color = self.NOTE_COLOR

        self.notes[note_id] = {
            "x": x,
            "y": y,
            "color": tuple(color),
            "highlight": False,
        }

        # Auto-scroll dopredu
        self.scroll_x = max(0, self.scroll_x + self.scroll_speed)

    def remove_note(self, event: Dict[str, Any]):
        track = event.get("track_id", 0)
        midi = event.get("note")
        t = event.get("time")

        if midi is None or t is None:
            return

        try:
            midi_int = int(midi)
        except Exception:
            return

        prefix = f"{track}_{midi_int}_{int(t * 1000)}"

        # nájdeme všetky ID začínajúce prefixom
        to_remove = [nid for nid in self.note_order if nid.startswith(prefix)]

        for nid in to_remove:
            self.notes.pop(nid, None)
            if nid in self.note_order:
                self.note_order.remove(nid)

    def highlight_note(self, note_id: str, color=None):
        if note_id in self.notes:
            self.notes[note_id]["color"] = tuple(color or self.HIGHLIGHT_COLOR)
            self.notes[note_id]["highlight"] = True

    def unhighlight_note(self, note_id: str):
        if note_id in self.notes:
            self.notes[note_id]["color"] = self.NOTE_COLOR
            self.notes[note_id]["highlight"] = False

    # ---------------------------------------------------------
    # MIDI → STAFF POSITION
    # ---------------------------------------------------------
    def _midi_to_staff_y(self, midi_note: int) -> int:
        """
        Jednoduché mapovanie MIDI výšky na notovú osnovu.
        C4 (60) je stred osnovy.
        Každý MIDI krok = ~3 pixely.
        """
        try:
            offset = int(midi_note) - 60
        except Exception:
            offset = 0

        return self.STAFF_TOP + 2 * self.STAFF_SPACING - offset * 3

    # ---------------------------------------------------------
    # DRAW STAFF
    # ---------------------------------------------------------
    def draw_staff(self, surface: pygame.Surface):
        w = surface.get_width()
        for i in range(self.STAFF_LINES):
            y = self.STAFF_TOP + i * self.STAFF_SPACING
            pygame.draw.line(
                surface,
                self.STAFF_LINE_COLOR,
                (20, y),
                (w - 20, y),
                2,
            )

    # ---------------------------------------------------------
    # DRAW NOTES
    # ---------------------------------------------------------
    def draw_notes(self, surface: pygame.Surface):
        w = surface.get_width()

        for note_id in list(self.note_order):
            note = self.notes.get(note_id)
            if not note:
                continue

            shifted_x = note["x"] - self.scroll_x

            # ignoruj noty mimo obrazovky
            if shifted_x < -50 or shifted_x > w + 50:
                continue

            color = note["color"]
            y = note["y"]

            pygame.draw.circle(surface, color, (shifted_x, y), self.NOTE_RADIUS)
            pygame.draw.circle(
                surface,
                self.NOTE_OUTLINE,
                (shifted_x, y),
                self.NOTE_RADIUS,
                2,
            )

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface: pygame.Surface):
        if surface is None:
            return

        surface.fill((25, 25, 25))

        self.draw_staff(surface)
        self.draw_notes(surface)
