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

    # ---------------------------------------------------------
    # API pre NotationProcessor / UIManager
    # ---------------------------------------------------------
    def add_note(self, note_id, x, y, color=None):
        """Pridá alebo aktualizuje notu na osnove."""
        self.notes[note_id] = {
            "x": x,
            "y": y,
            "color": color if color else self.NOTE_COLOR
        }

    def remove_note(self, note_id):
        if note_id in self.notes:
            del self.notes[note_id]

    def highlight_note(self, note_id, color=None):
        if note_id in self.notes:
            self.notes[note_id]["color"] = color if color else self.HIGHLIGHT_COLOR

    def unhighlight_note(self, note_id):
        if note_id in self.notes:
            self.notes[note_id]["color"] = self.NOTE_COLOR

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
