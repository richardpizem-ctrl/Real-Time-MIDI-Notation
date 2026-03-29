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

        self.notes = {}

        self.scroll_x = 0
        self.note_spacing = 22
        self.scroll_speed = 2

    def add_note(self, event):
        note_id = f"{event['track_id']}_{event['note']}_{event['time']}"

        x = len(self.notes) * self.note_spacing + 100

        midi_note = event["note"]
        y = self._midi_to_staff_y(midi_note)

        color = event.get("track_color", self.NOTE_COLOR)

        self.notes[note_id] = {
            "x": x,
            "y": y,
            "color": color
        }

        self.scroll_x += self.scroll_speed

    def remove_note(self, event):
        note_id = f"{event['track_id']}_{event['note']}_{event['time']}"
        if note_id in self.notes:
            del self.notes[note_id]

    def highlight_note(self, note_id, color=None):
        if note_id in self.notes:
            self.notes[note_id]["color"] = color or self.HIGHLIGHT_COLOR

    def unhighlight_note(self, note_id):
        if note_id in self.notes:
            self.notes[note_id]["color"] = self.NOTE_COLOR

    def _midi_to_staff_y(self, midi_note):
        offset = midi_note - 60
        return self.STAFF_TOP + 2 * self.STAFF_SPACING - offset * 3

    def draw_staff(self, surface):
        for i in range(self.STAFF_LINES):
            y = self.STAFF_TOP + i * self.STAFF_SPACING
            pygame.draw.line(surface, self.STAFF_LINE_COLOR, (20, y), (self.width - 20, y), 2)

    def draw_notes(self, surface):
        for note in self.notes.values():
            shifted_x = note["x"] - self.scroll_x
            pygame.draw.circle(surface, note["color"], (shifted_x, note["y"]), 7)

    def draw(self, surface):
        self.draw_staff(surface)
        self.draw_notes(surface)
