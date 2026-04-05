import pygame

class StaffUI:
    STAFF_LINE_COLOR = (220, 220, 220)
    NOTE_COLOR = (255, 255, 255)
    HIGHLIGHT_COLOR = (255, 80, 80)

    STAFF_TOP = 40
    STAFF_SPACING = 12
    STAFF_LINES = 5

    NOTE_RADIUS = 7
    NOTE_OUTLINE = (30, 30, 30)

    def __init__(self, width=1400, height=200):
        self.width = width
        self.height = height

        # note_id -> {x, y, color}
        self.notes = {}
        self.note_order = []  # stabilné poradie nôt

        # scrolling
        self.scroll_x = 0
        self.note_spacing = 22
        self.scroll_speed = 2

    # ---------------------------------------------------------
    # NOTE MANAGEMENT
    # ---------------------------------------------------------
    def add_note(self, event):
        """
        event:
            track_id
            note (MIDI)
            time
            track_color (optional)
        """
        note_id = f"{event['track_id']}_{event['note']}_{event['time']}"

        if note_id in self.notes:
            return  # nikdy neprepisujeme existujúcu notu

        self.note_order.append(note_id)

        # X pozícia podľa poradia
        x = len(self.note_order) * self.note_spacing + 100

        midi_note = event["note"]
        y = self._midi_to_staff_y(midi_note)

        color = event.get("track_color", self.NOTE_COLOR)

        self.notes[note_id] = {
            "x": x,
            "y": y,
            "color": color,
            "highlight": False
        }

        # Auto-scroll dopredu
        self.scroll_x = max(0, self.scroll_x + self.scroll_speed)

    def remove_note(self, event):
        note_id = f"{event['track_id']}_{event['note']}_{event['time']}"
        if note_id in self.notes:
            del self.notes[note_id]
        if note_id in self.note_order:
            self.note_order.remove(note_id)

    def highlight_note(self, note_id, color=None):
        if note_id in self.notes:
            self.notes[note_id]["color"] = color or self.HIGHLIGHT_COLOR
            self.notes[note_id]["highlight"] = True

    def unhighlight_note(self, note_id):
        if note_id in self.notes:
            self.notes[note_id]["color"] = self.NOTE_COLOR
            self.notes[note_id]["highlight"] = False

    # ---------------------------------------------------------
    # MIDI → STAFF POSITION
    # ---------------------------------------------------------
    def _midi_to_staff_y(self, midi_note):
        """
        Jednoduché mapovanie MIDI výšky na notovú osnovu.
        C4 (60) je stred osnovy.
        Každý MIDI krok = ~3 pixely.
        """
        offset = midi_note - 60
        return self.STAFF_TOP + 2 * self.STAFF_SPACING - offset * 3

    # ---------------------------------------------------------
    # DRAW STAFF
    # ---------------------------------------------------------
    def draw_staff(self, surface):
        for i in range(self.STAFF_LINES):
            y = self.STAFF_TOP + i * self.STAFF_SPACING
            pygame.draw.line(
                surface,
                self.STAFF_LINE_COLOR,
                (20, y),
                (self.width - 20, y),
                2
            )

    # ---------------------------------------------------------
    # DRAW NOTES
    # ---------------------------------------------------------
    def draw_notes(self, surface):
        for note_id in self.note_order:
            note = self.notes.get(note_id)
            if not note:
                continue

            shifted_x = note["x"] - self.scroll_x

            # ignoruj noty mimo obrazovky
            if shifted_x < -50 or shifted_x > self.width + 50:
                continue

            color = note["color"]
            y = note["y"]

            # telo noty
            pygame.draw.circle(surface, color, (shifted_x, y), self.NOTE_RADIUS)

            # outline
            pygame.draw.circle(surface, self.NOTE_OUTLINE, (shifted_x, y), self.NOTE_RADIUS, 2)

    # ---------------------------------------------------------
    # DRAW
    # ---------------------------------------------------------
    def draw(self, surface):
        # pozadie
        surface.fill((25, 25, 25))

        # osnova
        self.draw_staff(surface)

        # noty
        self.draw_notes(surface)
