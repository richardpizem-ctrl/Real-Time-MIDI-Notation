import pygame

class StaffUI:
    STAFF_LINE_COLOR = (220, 220, 220)
    NOTE_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 80, 80)

    STAFF_TOP = 40
    STAFF_SPACING = 12
    STAFF_LINES = 5

    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # Noty vo formáte: {note_id: {"x": int, "y": int, "color": (r,g,b)}}
        self.notes = {}

        # Posúvanie osnove
        self.scroll_x = 0
        self.note_spacing = 22  # horizontálny posun medzi notami

    # ---------------------------------------------------------
    # PREPOJENIE S EVENT ROUTEROM / TRACK SYSTEMOM
    # ---------------------------------------------------------
    def add_note(self, event):
        """
        event = dict z TrackSystemu:
        {
            "note": int,
            "track_color": (r,g,b),
            "time": float,
            ...
        }
        """

        note_id = f"{event['track_id']}_{event['note']}_{event['time']}"

        # X pozícia – posúvame sa doprava pri každej note
        x = 80 + len(self.notes) * self.note_spacing - self.scroll_x

        # Y pozícia – jednoduché mapovanie MIDI noty na osnovu
        midi_note = event["note"]
        y = self._midi_to_staff_y(midi_note)

        color = event.get("track_color", self.NOTE_COLOR)

        self.notes[note_id] = {
            "x": x,
            "y": y,
            "color": color
        }

    def remove_note(self, event):
        """Odstráni notu podľa eventu."""
        to_delete = []

        for note_id, data in self.notes.items():
            if note_id.startswith(f"{event['track_id']}_{event['note']}"):
                to_delete.append(note_id)

        for note_id in to_delete:
            del self.notes[note_id]

    # ---------------------------------------------------------
    # HIGHLIGHT API
    # ---------------------------------------------------------
    def highlight_note(self, note_id, color=None):
        if note_id in self.notes:
            self.notes[note_id]["color"] = color if color else self.HIGHLIGHT_COLOR

    def unhighlight_note(self, note_id):
        if note_id in self.notes:
            self.notes[note_id]["color"] = self.NOTE_COLOR

    # ---------------------------------------------------------
    # MIDI → STAFF Y MAPOVANIE
    # ---------------------------------------------------------
    def _midi_to_staff_y(self, midi_note):
        """
        Jednoduché mapovanie MIDI noty na osnovu.
        Neskôr sa môže nahradiť skutočným notovým systémom.
        """
        # C4 = 60 → stred osnovy
        offset = midi_note - 60
        return self.STAFF_TOP + 2 * self.STAFF_SPACING - offset * 3

    # ---------------------------------------------------------
    # KRESLENIE OSNOVY
    # ---------------------------------------------------------
    def draw_staff(self, surface):
        for i in range(self.STAFF_LINES):
            y = self.STAFF_TOP + i * self.STAFF_SPACING
            pygame.draw.line(surface, self.STAFF_LINE_COLOR, (20, y), (self.width - 20, y), 2)

    # ---------------------------------------------------------
    # KRESLENIE NÔT
    # ---------------------------------------------------------
    def draw_notes(self, surface):
        for note in self.notes.values():
            pygame.draw.circle(surface, note["color"], (note["x"], note["y"]), 7)

    # ---------------------------------------------------------
    # HLAVNÁ DRAW FUNKCIA
    # ---------------------------------------------------------
    def draw(self, surface):
        self.draw_staff(surface)
        self.draw_notes(surface)
